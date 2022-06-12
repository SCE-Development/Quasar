from flask import Flask
import json
import sys

app = Flask(__name__)

@app.route("/")
def api():
    return (json.dumps(
            {"left" : {"up" : True, "inkLevel" : 60},
             "right": {"up" : True, "inkLevel" : 70}}),
            200,
            {'Content-Type' : 'application/json'})
        

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=int(sys.argv[1]))


