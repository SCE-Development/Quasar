import enum

import prometheus_client


class Metrics(enum.Enum):
    # name, desc, type, labelnames=()
    # above default value referenced from the metrics constructor
    # in the prometheus_client library, see
    # https://github.com/prometheus/client_python/blob/fd4da6cde36a1c278070cf18b4b9f72956774b05/prometheus_client/metrics.py#L115
    PRINT_JOBS_RECIEVED = (
        "print_jobs_recieved",
        "number of urls asked to play from the frontend",
        prometheus_client.Counter,
    )
    LAST_HEALTH_CHECK_REQUEST = (
        "last_health_check_request",
        "total bytes of files pointed to by cache",
        prometheus_client.Gauge,
    )
    SSH_TUNNEL_LAST_OPENED = (
        "ssh_tunnel_last_opened",
        "total bytes of files pointed to by cache",
        prometheus_client.Gauge,
    )

    def __init__(self, title, description, prometheus_type, labels=()):
        # we use the above default value for labels because it matches what's used
        # in the prometheus_client library's metrics constructor, see
        # https://github.com/prometheus/client_python/blob/fd4da6cde36a1c278070cf18b4b9f72956774b05/prometheus_client/metrics.py#L115
        self.title = title
        self.description = description
        self.prometheus_type = prometheus_type
        self.labels = labels


class MetricsHandler:
    _instance = None

    def __init__(self):
        raise RuntimeError('Call MetricsHandler.instance() instead')
    
    def init(self) -> None:
        for metric in Metrics:
            setattr(
                self,
                metric.title,
                metric.prometheus_type(
                    metric.title, metric.description, labelnames=metric.labels
                ),
            )

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls.init(cls)
            # Put any initialization here.
        return cls._instance
