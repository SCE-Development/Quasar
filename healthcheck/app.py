from flask import Flask, jsonify, Response
import requests
import json
import sys
from urllib.parse import urljoin
import time
import prometheus_client

app = Flask(__name__)

last_acccess = prometheus_client.Gauge(
    "last_accessed",
    "last time accessed",
)

@app.route("/healthcheck/printer")
def api():
    metric = time.time()
    last_acccess.set(metric)
    return jsonify({"last_accessed": metric})
    
@app.route('/metrics')
def get_metrics():
    return Response(
        prometheus_client.generate_latest(),
        mimetype="text/plain"
    )

if __name__ == "__main__":
    port = 14000
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    # TODO: Turn these params into argparse values
    app.run(host='127.0.0.1', port=port)
