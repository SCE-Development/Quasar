import time
import argparse
from threading import Thread
import enum
import logging

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import prometheus_client
from pysnmp.hlapi import *
import uvicorn

# from modules.metrics import (
#     page_count_metric,
#     ink_percent_metric,
#     snmp_req_duration
# )

page_count_metric = prometheus_client.Gauge(
    "page_count",
    "Number of pages printed",
)

ink_percent_metric = prometheus_client.Gauge(
    "ink_percent",
    "Percentage of ink remaining",
)

snmp_req_duration = prometheus_client.Gauge(
    "snmp_request_duration",
    "Time it took for SNMP request",
)


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

class SnmpOid(enum.Enum):
    INK_LEVEL = "1.3.6.1.2.1.43.11.1.1.9.1.1"
    INK_CAPACITY = "1.3.6.1.2.1.43.11.1.1.8.1.1"
    PAGE_COUNT = "1.3.6.1.2.1.43.10.2.1.4.1.1"

def get_snmp_data(ip, oid):
    start = time.time()
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData('public', mpModel=0),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )
    
    snmp_req_duration.set(time.time() - start)

    if errorIndication: 
        print(f"Error: {errorIndication}")
        return None
    elif errorStatus:
        print(f"Error: {errorStatus.prettyPrint()} at {errorIndex}")
        return None
    else:
        for res in varBinds:
            return res[1]

def update_metrics(ip):
    while True:
        ink_level = get_snmp_data(ip, SnmpOid.INK_LEVEL.value)
        ink_cap = get_snmp_data(ip, SnmpOid.INK_CAPACITY.value)
        page_count = get_snmp_data(ip, SnmpOid.PAGE_COUNT.value)

        if ink_level and ink_cap:
            ink_percent = float(ink_level) / float(ink_cap)
            ink_percent_metric.set(ink_percent)
            

        if page_count:
            logging.info('setting')
            page_count_metric.set(int(page_count))

        logging.info(f"SNMP data Ink capacity: {ink_cap}, Page !!: {(bool(page_count), int(page_count), page_count)}")
        print(ink_percent)

        time.sleep(2)

@app.get("/metrics")
async def metrics():
    return Response(
        content=prometheus_client.generate_latest(),
        media_type="text/plain",
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser("snmp coolness")

    parser.add_argument(
        "--ip",
        help="IP address of snmp agent (default: 192.168.69.208)",
        default="192.168.69.208"
    )
    parser.add_argument(
        "--host",
        help="ip address to listen for requests on, i.e. 0.0.0.0",
        default='0.0.0.0',
    )
    parser.add_argument(
        "--port",
        type=int,
        help="port for the server to listen on, default is 5000",
        default=5000
    )

    args = parser.parse_args()

    thread = Thread(target = update_metrics, args = (args.ip,), daemon=True)
    thread.start()
    uvicorn.run(
        app, 
        host=args.host, 
        port=args.port, 
        # reload=True,
    )
