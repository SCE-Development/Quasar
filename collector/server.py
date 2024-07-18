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

snmp_metric = prometheus_client.Gauge(
    "snmp_metric",
    "ex: Number of pages printed",
    ["name"],
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
    INK_LEVEL = ("ink_level","1.3.6.1.2.1.43.11.1.1.9.1.1")
    INK_CAPACITY = ("ink_capacity","1.3.6.1.2.1.43.11.1.1.8.1.1")
    PAGE_COUNT = ("page_count","1.3.6.1.2.1.43.10.2.1.4.1.1")
    DOOR_STATUS = ("door_status","1.3.6.1.2.1.43.18.1.1.2.1.12")
    TRAY_STATUS = ("tray_status","1.3.6.1.2.1.43.18.1.1.2.1.9")

    def __init__(self, metric_name, metric_value):
        self.metric_name = metric_name
        self.metric_value = metric_value

def get_snmp_data(ip):
    ink_level = 0
    ink_cap = 0
    for oid in SnmpOid:
        start = time.time()
        errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData('public', mpModel=0),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid.metric_value)))
        )
        snmp_req_duration.set(time.time() - start)
        if errorIndication:
            logging.error(f"Error: {errorIndication}")
        elif errorStatus:
            logging.error(f"Error: {errorStatus.prettyPrint()}")
        else:
            for res in varBinds:
                if (res[1] == 3) and oid.metric_name == "door_status":
                    snmp_metric.labels(name="door_status").set(1)
                elif (res[1] == 3) and oid.metric_name == "tray_status":
                    snmp_metric.labels(name="tray_status").set(1)
                else:
                    snmp_metric.labels(name=oid.metric_name).set(res[1])
                if oid.metric_name == "ink_level":
                    ink_level = res[1]
                elif oid.metric_name == "ink_capacity":
                    ink_cap = res[1]
    if ink_cap:
        snmp_metric.labels(name="ink_percent").set(ink_level/ink_cap)
    
    time.sleep((args.sleep_duration_minutes)*60)

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
    parser.add_argument(
        "--sleep-duration-minutes",
        type=int,
        help="update sleepy time, default is 2mins",
        default=2
    )
    snmp_metric.labels(name="tray_status").set(0)
    snmp_metric.labels(name="door_status").set(0)
    args = parser.parse_args()

    thread = Thread(target = get_snmp_data, args = (args.ip,), daemon=True)
    thread.start()
    uvicorn.run(
        app, 
        host=args.host, 
        port=args.port, 
        # reload=True,
    )
