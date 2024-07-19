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

snmp_metric = prometheus_client.Gauge(
    "snmp_metric",
    "ex: Number of pages printed",
    ["name"],
)

snmp_error = prometheus_client.Gauge(
    "snmp_error",
    "Error metrics",
    ["name"],
)

snmp_req_duration = prometheus_client.Summary(
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
    INK_LEVEL = ("ink_level", "1.3.6.1.2.1.43.11.1.1.9.1.1")
    INK_CAPACITY = ("ink_capacity", "1.3.6.1.2.1.43.11.1.1.8.1.1")
    PAGE_COUNT = ("page_count", "1.3.6.1.2.1.43.10.2.1.4.1.1")
    DOOR_STATUS = ("door_status", "1.3.6.1.2.1.43.18.1.1.2.1.12", True)
    TRAY_STATUS = ("tray_status", "1.3.6.1.2.1.43.18.1.1.2.1.9", True)

    def __init__(self, metric_name, metric_value, is_error):
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.is_error = is_error

def get_snmp_data(ip):
    while True:
        for oid in SnmpOid:
            with snmp_req_duration.time():
                errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(SnmpEngine(),
                CommunityData('public', mpModel=0),
                UdpTransportTarget((ip, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(oid.metric_value)))
                )
                if errorIndication:
                    logging.error(f"Error: {errorIndication}")
                elif errorStatus:
                    logging.error(f"Error: {errorStatus.prettyPrint()}")
                else:
                    for res in varBinds:
                        if oid.is_error:
                            snmp_error.labels(name=oid.metric_name).set(int(res[1] == 3))
                            continue
                        snmp_metric.labels(name=oid.metric_name).set(res[1])
        time.sleep(args.sleep_duration_minutes * 60)

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

    args = parser.parse_args()

    snmp_error.labels(name="tray_status").set(0)
    snmp_error.labels(name="ink_status").set(0)
    thread = Thread(target = get_snmp_data, args = (args.ip,), daemon=True)
    thread.start()
    uvicorn.run(
        app, 
        host=args.host, 
        port=args.port, 
        # reload=True,
    )
