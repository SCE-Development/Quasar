import time
import enum
import logging
import json
import asyncio

from pysnmp.hlapi import *

from modules.metrics import MetricsHandler

metrics_handler = MetricsHandler.instance()


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


def fetch_ips_from_config(config_file_path):
    try:
        with open(config_file_path, "r") as f:
            config = json.load(f)
            printer_configs = config.get("PRINTING")
            if not printer_configs:
                raise Exception("No printers defined in config file")

            ip_list = []
            for printer in printer_configs:
                if isinstance(printer_configs[printer], dict):
                    ip = printer_configs[printer]["IP"]
                    logging.info(f"Adding printer {printer} with IP {ip}")
                    ip_list.append(ip)
            return ip_list

    except Exception as e:
        logging.error(f"error opening config file: {e}")


def scrape_snmp(ip_list, sleep_duration_minutes=5):
    while True:
        for ip in ip_list:
            get_snmp_data(ip)
        time.sleep(sleep_duration_minutes * 60)


def get_snmp_data(ip):
    for oid in SnmpOid:
        with metrics_handler.snmp_request_duration.time():
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(
                    SnmpEngine(),
                    CommunityData("public", mpModel=0),
                    UdpTransportTarget((ip, 161)),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid.metric_value)),
                )
            )
        if errorIndication:
            logging.error(
                f"Error indication from {ip} for metric {oid.metric_value}: {errorIndication}"
            )
            metrics_handler.device_unreachable.set(1)
            continue
        if errorStatus:
            logging.error(
                f"Error status from {ip} for metric {oid.metric_value}: {errorStatus.prettyPrint()}"
            )
            # SNMP OIDs related to errors often dissappear when
            # the associated issue that the metric refers to is
            # no longer present (i.e. an empty tray now has
            # paper). To avoid leaving an error metric as 1
            # which would create a false positive, set the metric
            # to zero if the associated SNMP OID was not found
            if oid.is_error:
                metrics_handler.snmp_error.labels(name=oid.metric_name, ip=ip).set(0)
            continue

        metrics_handler.device_unreachable.set(0)
        if not varBinds:
            continue
        res = varBinds[0]
        if oid.is_error:
            metrics_handler.snmp_error.labels(name=oid.metric_name, ip=ip).set(1)
            continue
        metrics_handler.snmp_metric.labels(name=oid.metric_name, ip=ip).set(res[1])
