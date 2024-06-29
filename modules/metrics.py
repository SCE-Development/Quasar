import prometheus_client

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