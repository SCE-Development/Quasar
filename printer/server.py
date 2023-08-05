import argparse
import base64
import json
import os
import pathlib
import subprocess
import threading
import time
import uuid


from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from prometheus_client import Gauge, generate_latest


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

neel1 = Gauge('neel1', '1 if up 0 if not')
ssh_tunnel_last_opened = Gauge('ssh_tunnel_last_opened', 'the last time we opened the ssh tunnel')


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="host name for server to listen on. defaults to 0.0.0.0"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9000,
        help="PORT name for server to listen on. defaults to 9000"
    )
    parser.add_argument(
        "--config-json-path",
        default="/app/config/config.json",
        help="path to config json path"
    )
    parser.add_argument(
        "--development",
        action="store_true",
        default=False,
        help="specify if server should run in development. this means requests won't get sent to a printer but logger instead"
    )
    return parser.parse_args()

args = get_args()

with open(args.config_json_path) as json_file:
    config_json = json.load(json_file)
    printerLeftName = config_json.get("PRINTING", {}).get("LEFT", {}).get("NAME")

def maybe_reopen_ssh_tunnel():
    """
    if we havent recieved a health check ping in over 1 min then
    we rerun the script to open the ssh tunnel.
    """
    while 1:
        print("reponing gang", neel1._value.get(), now_epoch_seconds)
        time.sleep(60)
        now_epoch_seconds = int(time.time())
        # skip reopening the tunnel if the value is 0 or falsy
        if not neel1._value.get():
            continue
        if now_epoch_seconds - neel1._value.get() > 120:
            ssh_tunnel_last_opened.set(now_epoch_seconds)
            subprocess.Popen(
                './what.sh tunnel-only',
                shell=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            )

@app.get("/healthcheck/printer")
def api():
    return "printer is up!"

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
      # `-o page-ranges=<whatever user sent>` OR is it `-P <whatever user sent>`
      # -n <pages>
      if missing_required_keys:
        return HTTPException(
           status_code=400,
           detail="fields raw copies and pageRanges must be present in JSON body",
        )
    except json.decoder.JSONDecodeError:
      return HTTPException(status_code=400, detail="could not parse JSON body")
    
    print(data)
    
    
    # make a curl command to test this
    """
    curl --location --request POST 'localhost:9000/print' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "raw": "YWtzaGl0Cg==",
        "copies": 1
    }'
    """
    base = pathlib.Path("/tmp")
    file_id = str(uuid.uuid4())
    file_path = str(base / file_id)
    decoded = base64.b64decode(data['raw'])
    open(file_path, 'wb').write(decoded)

    # make a function that takes in file path, copies, and optional page range
    # and it prints the below string:
    """
    lp -n <copies> <maybe insert page ranges here> -o sides=one-sided -o media=na_letter_8.5x11in -d PENIS <file_path>

    <maybe insert page ranges here> can be empty string if page range wasnt sent, else -o page-ranges=<whatever user sent>
    """
    print(temp(file_path, int(data['copies']), page_range=data.get("pageRanges")))
    text_content = pathlib.Path(file_path).read_text()
    pathlib.Path(file_path).unlink(missing_ok=False)
    return text_content

@app.get("/metrics")
def metrics():
    return generate_latest()


if __name__  == "__main__":
    print("yoyoyo!!!!!", flush=True)
    uvicorn.run("server:app", host=args.host, port=args.port, reload=True)

def temp(file_path: str, num_copies: int, page_range: str = None) -> str:
    maybe_page_range = ''
    if page_range:
       maybe_page_range = f'-o page-ranges={page_range}'
    t = threading.Thread(
        target=maybe_reopen_ssh_tunnel,
        daemon=True,
    )
    t.start()
    print("lp -n {num_copies} {maybe_page_range} -o sides=one-sided -o media=na_letter_8.5x11in -d {printerLeftName} {file_path}")
    os.popen(f"lp -n {num_copies} {maybe_page_range} -o sides=one-sided -o media=na_letter_8.5x11in -d {printerLeftName} {file_path}")

    


# delete the file after printing
# 6. add thread that checks ssh tunnel being open, reopen if died (just like led sign)
# 7. os.popen
# add logging, argparse for level
# right printer only!
