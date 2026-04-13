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


def make_signature(access_key: str, secret_key: str, req_time: str, request_param: str) -> str:
    payload = f"{access_key}{req_time}{request_param}"
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
            "error": "No JSON received from TradingView",
            "raw_body": request.get_data(as_text=True)
        }), 400

    side = data.get("side")
    symbol = "XAUT_USDT"

    if side == "buy":
        order_side = 1
    elif side == "sell":
        order_side = 2
    else:
        return jsonify({
            "error": "invalid side",
            "received_side": side
        }), 400

    params = {
        "symbol": symbol,
        "price": 0,
        "vol": 1,
        "side": order_side,
        "type": 1,
        "openType": 1,
        "leverage": 5,
        "externalOid": str(int(time.time()))
    }

    request_param = json.dumps(params, separators=(",", ":"), ensure_ascii=False)
    req_time = str(int(time.time() * 1000))
    signature = make_signature(API_KEY, API_SECRET, req_time, request_param)

    headers = {
        "Content-Type": "application/json",
        "ApiKey": API_KEY,
        "Request-Time": req_time,
        "Signature": signature,
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/private/order/submit",
            data=request_param,
            headers=headers,
            timeout=15
        )
    except requests.RequestException as e:
        print("REQUEST ERROR:", str(e), flush=True)
        return jsonify({
            "step": "request_to_mexc_failed",
            "details": str(e)
        }), 500

    try:
        mexc_json = response.json()
    except ValueError:
        mexc_json = None

    print("TradingView data:", data, flush=True)
    print("MEXC status:", response.status_code, flush=True)
    print("MEXC response text:", response.text, flush=True)

    return jsonify({
        "ok": response.ok,
        "status_code": response.status_code,
        "mexc_json": mexc_json,
        "mexc_text": response.text
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
