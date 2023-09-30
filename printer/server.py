import argparse
import base64
import json
import logging
import os
import pathlib
import subprocess
import threading
import time
import uuid

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import prometheus_client
import uvicorn

from metrics import MetricsHandler


metrics_handler = MetricsHandler.instance()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(
    format="%(asctime)s.%(msecs)03dZ %(processName)s %(threadName)s %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)


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
    return parser.parse_args()


args = get_args()

# only the right printer works right now, so we default to it
PRINTER_NAME = os.environ.get("RIGHT_PRINTER_NAME")


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
    file_path: str, num_copies: int, page_range: str = None
) -> str:
    maybe_page_range = ""
    if page_range:
        # to speciy page ranges, we can do:
        # `-o page-ranges=<whatever user sent>` OR `-P <whatever user sent>`
        maybe_page_range = f"-o page-ranges={page_range}"
    command = f"lp -n {num_copies} {maybe_page_range} -o sides=one-sided -o media=na_letter_8.5x11in -d {PRINTER_NAME} {file_path}"
    metrics_handler.print_jobs_recieved.inc()
    if args.development:
        logging.warning(f"server is in development mode, command would've been `{command}`")
    else:
        print_job = subprocess.Popen(
            command,
            shell=True,
        )
        print_job.wait()


@app.get("/healthcheck/printer")
def api():
    metrics_handler.last_health_check_request.set(int(time.time()))
    return "printer is up!"

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return prometheus_client.generate_latest()


@app.post("/print")
async def read_item(request: Request):
    """
    incoming request to print looks like
    {
      "raw": base64 encoded file data
      "copies": integer or whatever, we insert this into the lp command,
      "pageRanges": string value from user input on clark frontend; we insert this into the lp command,
    }
    """
    try:
        data = await request.json()
        missing_required_keys = not all(key in data for key in ["raw", "copies"])
        if missing_required_keys:
            return HTTPException(
                status_code=400,
                detail="fields raw copies and pageRanges must be present in JSON body",
            )
    except json.decoder.JSONDecodeError:
        return HTTPException(status_code=400, detail="could not parse JSON body")

    try:
        base = pathlib.Path("/tmp")
        file_id = str(uuid.uuid4())
        file_path = str(base / file_id)
        decoded = base64.b64decode(data["raw"])
        with open(file_path, "wb") as f:
            f.write(decoded)

        send_file_to_printer(
            file_path, int(data["copies"]), page_range=data.get("pageRanges")
        )
        pathlib.Path(file_path).unlink()
        return "worked!"
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

if __name__ == "__main__":
    uvicorn.run("server:app", host=args.host, port=args.port, reload=True)
