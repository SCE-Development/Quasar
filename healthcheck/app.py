from flask import Flask, jsonify, Response
import requests
import argparse
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port', 
        metavar='port', 
        type=int, 
        default=14000, 
        help='enter port'
    )
    parser.add_argument(
        '--host', 
        metavar='host', 
        type=str, 
        default='127.0.0.1', 
        help='host address'
    )
    args = parser.parse_args()
    app.run(host=args.host, port=args.port)
