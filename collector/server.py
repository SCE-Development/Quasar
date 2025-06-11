import time
import argparse
from threading import Thread
import enum
import logging
import json

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import prometheus_client
from pysnmp.hlapi import *
import uvicorn

snmp_metric = prometheus_client.Gauge(
    "snmp_metric",
    "ex: Number of pages printed",
    ["name", "ip"],
)

snmp_error = prometheus_client.Gauge(
    "snmp_error",
    "Error metrics",
    ["name", "ip"],
)

snmp_req_duration = prometheus_client.Summary(
    "snmp_request_duration",
    "Time it took for SNMP request",
)

device_unreachable = prometheus_client.Gauge(
    "device_unreachable",
    "set to 1 when error",
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
    TRAY_EMPTY = ("tray_empty", "1.3.6.1.2.1.43.18.1.1.8.1.13", True)
    # we observed each printer emitting a different SNMP OID for
    # an empty paper tray, the below accounts for this second OID.
    # the _2 at the end of this metric does imply that the printer has
    # 2 trays. tray_empty_2 is an indication of the same exact issue
    # as tray_empty: an empty paper tray.
    TRAY_EMPTY_2 = ("tray_empty_2", "1.3.6.1.2.1.43.18.1.1.8.1.2", True)

    def __init__(self, metric_name, metric_value, is_error=False):
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.is_error = is_error

def scrape_snmp(ip_list):
    while True:
        for ip in ip_list:
            get_snmp_data(ip)
        time.sleep(args.sleep_duration_minutes * 60)

def get_snmp_data(ip):
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
            logging.error(f"Error indication from {ip} for metric {oid.metric_value}: {errorIndication}")
            device_unreachable.set(1)
            continue
        if errorStatus:
            logging.error(f"Error status from {ip} for metric {oid.metric_value}: {errorStatus.prettyPrint()}")
            # SNMP OIDs related to errors often dissappear when
            # the associated issue that the metric refers to is
            # no longer present (i.e. an empty tray now has
            # paper). To avoid leaving an error metric as 1
            # which would create a false positive, set the metric
            # to zero if the associated SNMP OID was not found
            if oid.is_error:
                snmp_error.labels(name=oid.metric_name, ip=ip).set(0)
            continue

        device_unreachable.set(0)
        if not varBinds:
            continue
        res = varBinds[0]
        if oid.is_error:
            snmp_error.labels(name=oid.metric_name, ip=ip).set(1)
            continue
        snmp_metric.labels(name=oid.metric_name, ip=ip).set(res[1])

@app.get("/metrics")
async def metrics():
    return Response(
        content=prometheus_client.generate_latest(),
        media_type="text/plain",
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser("snmp coolness")

    parser.add_argument(
        "--ips",
        help="List of IP addresses of snmp agent (default: 192.168.69.208,192.168.69.149)",
        default="192.168.69.208,192.168.69.149"
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
    try:
        with open("/tmp/config.json", "r") as f:
            config = json.load(f)
            left_ip = config["PRINTING"]["LEFT"]["IP"]
            right_ip = config["PRINTING"]["RIGHT"]["IP"]
            ip_list=[left_ip, right_ip]

            logging.info(f"connected to left printer ip: {left_ip}")
            logging.info(f"connected to right printer ip: {right_ip}")   
            thread = Thread(target = scrape_snmp, args=(ip_list,), daemon=True)
            thread.start()
    except Exception as e:
        logging.error(f"error opening config file: {e}")

    uvicorn.run(
        app, 
        host=args.host, 
        port=args.port, 
        # reload=True,
    )
