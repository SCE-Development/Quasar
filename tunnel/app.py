from flask import Flask
import json
import sys

app = Flask(__name__)

@app.route("/")
def api():
    return "Hello from Quasar!"
        

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=int(sys.argv[1]))


