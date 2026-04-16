from flask import Flask, request, jsonify
import requests
import time
import hmac
import hashlib
import json

app = Flask(__name__)

API_KEY = "mx0vgl74MjSCVgG712"
API_SECRET = "15d9c38c65fd4062afaab277f07ad63d"

BASE_URL = "https://contract.mexc.com"


def make_signature(api_key, secret_key, req_time, request_param):
    payload = f"{api_key}{req_time}{request_param}"
    return hmac.new(
        secret_key.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


@app.route("/")
def home():
    return "Bot running 🚀"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "No JSON received",
            "raw": request.get_data(as_text=True)
        }), 400

    side = data.get("side")

    if side == "buy":
        order_side = 1
    elif side == "sell":
        order_side = 2
    else:
        return jsonify({"error": "Invalid side"}), 400

    params = {
        "symbol": "XAUT_USDT",
        "price": 0,
        "vol": 1,
        "side": order_side,
        "type": 1,
        "openType": 1,
        "leverage": 5,
        "externalOid": str(int(time.time()))
    }

    request_param = json.dumps(params)
    req_time = str(int(time.time() * 1000))
    signature = make_signature(API_KEY, API_SECRET, req_time, request_param)

    headers = {
        "Content-Type": "application/json",
        "ApiKey": API_KEY,
        "Request-Time": req_time,
        "Signature": signature
    }

    try:
        response = requests.post(
            BASE_URL + "/api/v1/private/order/submit",
            json=params,
            headers=headers,
            timeout=15
        )

        print("TradingView:", data, flush=True)
        print("STATUS:", response.status_code, flush=True)
        print("RESPONSE:", response.text, flush=True)

        return jsonify({
            "status": response.status_code,
            "response": response.text
        })

    except Exception as e:
        print("ERROR:", str(e), flush=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
