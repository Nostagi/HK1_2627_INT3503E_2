# Hello API

from flask import Flask, jsonify, request

app = Flask(__name__)

LOCALHOST:dict = {
    "host" : "127.0.0.1",
    "port" : 5000,
    "debug" : True      # only for localhost3
}

# ----------------------

@app.route("/")
def index():
    return {
        "message": "Hello API~~"
    }


@app.route("/health", methods=['GET'])
def health():
    return jsonify({"status": "OK"}), 200


@app.route("/echo", methods=['POST'])
def echo():
    # silent == trả None nếu không phải JSON (Content-type: application/json).
    # not silent == raise HTTP Error 400
    data = request.get_json(silent=True) or {}

    return jsonify({"you_sent": data}), 200


# ---------------------

if __name__ == "__main__":
    app.run(
        **LOCALHOST
    )


