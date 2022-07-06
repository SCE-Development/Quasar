from flask import Flask, jsonify
import requests
import json
import sys

app = Flask(__name__)

@app.route("/healthcheck/printer")
def api():
    return "printer is up!"

@app.route("/healthcheck/ledsign")
def ledsign_health_api():
    with open("/app/config/config.json", "r") as file:
        led_url = json.load(file)["LED_URL"]

    try:
        resp = requests.get(led_url + "/api/health-check")
    except requests.exceptions.ConnectionError:
        return jsonify({"success" : False})

    return (resp.text, resp.status_code, resp.headers.items())
        

if __name__ == "__main__":
    port = 14000
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    # TODO: Turn these params into argparse values
    app.run(host='127.0.0.1', port=port)
