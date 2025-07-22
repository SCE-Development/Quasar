import argparse
import logging
import os
import pathlib
import subprocess
import threading
import time
import uuid
import collector

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import prometheus_client
import uvicorn

from metrics import MetricsHandler
import sqlite_helpers


metrics_handler = MetricsHandler.instance()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(
    # in mondo we trust
    format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="host name for server to listen on. defaults to 0.0.0.0",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9000,
        help="PORT name for server to listen on. defaults to 9000",
    )
    parser.add_argument(
        "--config-json-path",
        default="/app/config/config.json",
        help="path to config json path",
    )
    parser.add_argument(
        "--development",
        action="store_true",
        default=False,
        help="specify if server should run in development. this means requests won't get sent to a printer but logger instead",
    )
    parser.add_argument(
        "--dont-delete-pdfs",
        action="store_true",
        default=False,
        help="specify if server should delete pdfs after printing",
    )
    parser.add_argument(
        "--sleep-duration-minutes",
        type=int,
        help="update sleepy time, default is 2mins",
        default=2,
    )
    parser.add_argument(
        "--database-file-path",
        required=True,
        help="path to sqlite database file"
    )
    return parser.parse_args()


args = get_args()


def maybe_reopen_ssh_tunnel():
    """
    if we havent recieved a health check ping in over 1 min then
    we rerun the script to open the ssh tunnel.
    """
    while 1:
        time.sleep(60)
        now_epoch_seconds = int(time.time())
        last_health_check = metrics_handler.last_health_check_request._value.get()
        if now_epoch_seconds - last_health_check > 120:
            metrics_handler.ssh_tunnel_last_opened.set(int(time.time()))
            logging.warning(
                f"now_epoch_seconds - last_health_check = {now_epoch_seconds - last_health_check}, reopening SSH tunnel"
            )
            subprocess.Popen(
                "./what.sh --tunnel-only",
                shell=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            )


def send_file_to_printer(
    file_path: str, num_copies: int, page_range: str = None, sides: str = "one-sided"
) -> str:
    maybe_page_range = ""
    if page_range:
        # to speciy page ranges, we can do:
        # `-o page-ranges=<whatever user sent>` OR `-P <whatever user sent>`
        maybe_page_range = f"-o page-ranges={page_range}"

    # only the right printer works right now, so we default to it
    PRINTER_NAME = os.environ.get("RIGHT_PRINTER_NAME")
    command = f"lp -n {num_copies} {maybe_page_range} -o sides={sides} -o media=na_letter_8.5x11in -d {PRINTER_NAME} {file_path}"
    metrics_handler.print_jobs_recieved.inc()
    if args.development:
        logging.warning(
            f"server is in development mode, command would've been `{command}`"
        )
        return None

    print_job = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    print_job.wait()

    if print_job.returncode != 0:
        logging.error(
            f"command returned code {print_job.returncode} stderr: {print_job.stderr.read()} stdout: {print_job.stdout.read()}"
        )
        return None
    try:
        print_id = print_job.stdout.read().strip().split(" ")[3]
        sqlite_helpers.insert_print_job(args.database_file_path, print_id)
        logging.info(f"extracted print id is {print_id}")
        return print_id
    except Exception:
        logging.exception(
            f"failed to extract print id from stdout: {print_job.stdout.read()}"
        )
        # need to find a better value to return when the command exited
        # with code 0 but the output could not be parsed for a job id.
        return ''


def maybe_delete_pdf(file_path):
    if args.dont_delete_pdfs:
        logging.info(
            f"--dont-delete-pdfs is set, skipping deletion of file {file_path}"
        )
        return
    pathlib.Path(file_path).unlink()


@app.get("/healthcheck/printer")
def api():
    metrics_handler.last_health_check_request.set(int(time.time()))
    return "printer is up!"


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return prometheus_client.generate_latest()


@app.post("/print")
async def read_item(
    file: UploadFile = File(...), copies: str = Form(...), sides: str = Form(...)
):
    """
    incoming request to print looks like
    {
      "file": file data
      "copies": integer or whatever, we insert this into the lp command,
      "sides": string value from user input on clark frontend; we insert this into the lp command,
    }
    """
    try:
        base = pathlib.Path("/tmp")
        file_id = str(uuid.uuid4())
        file_path = str(base / file_id)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        print_id = send_file_to_printer(
            str(file_path),
            copies,
            sides=sides,
        )

        maybe_delete_pdf(file_path)

        if not args.development and print_id is None:
            raise Exception("unable to extract print id from print request")
        return {"print_id": print_id}
    except Exception:
        logging.exception("printing failed!")
        return HTTPException(
            status_code=500,
            detail="printing failed, check logs",
        )


# we have a separate __name__ check here due to how FastAPI starts
# a server. the file is first ran (where __name__ == "__main__")
# and then calls `uvicorn.run`. the call to run() reruns the file,
# this time __name__ == "server". the separate __name__ if statement
# is so the thread references the same instance as the global
# metrics_handler referenced by the rest of the file. otherwise,
# the thread interacts with an instance different than the one the
# server uses
if __name__ == "server":
    if not args.development:
        # set the last time we opened an ssh tunnel to now because
        # when the script runs for the first time, we did so in what.sh
        metrics_handler.ssh_tunnel_last_opened.set(int(time.time()))
        t = threading.Thread(
            target=maybe_reopen_ssh_tunnel,
            daemon=True,
        )
        t.start()
 
        sqlite_helpers.maybe_create_table(args.database_file_path)  

        if not args.development and os.path.exists(args.config_json_path):
            thread = threading.Thread(
                target=collector.scrape_snmp,
                args=(
                    collector.fetch_ips_from_config(args.config_json_path),
                    args.sleep_duration_minutes,
                ),
                daemon=True,
            )
            thread.start()

if __name__ == "__main__":
    uvicorn.run("server:app", host=args.host, port=args.port, reload=True)
