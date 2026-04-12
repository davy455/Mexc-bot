from flask import Flask, request, jsonify
import requests
import time
import hmac
import hashlib

app = Flask(__name__)

API_KEY = "mx0vgl74MjSCVgG712"
API_SECRET = "15d9c38c65fd4062afaab277f07ad63d"

BASE_URL = "https://contract.mexc.com"


def sign(params: dict) -> str:
    query = "&".join([f"{k}={v}" for k, v in params.items()])
    return hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()


@app.route("/")
def home():
    return "Bot running 🚀"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if data is None:
        raw_body = request.get_data(as_text=True)
        return jsonify({
            "error": "No JSON received from TradingView",
            "raw_body": raw_body
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

    params["sign"] = sign(params)

    headers = {
        "ApiKey": API_KEY
    }

    try:
        response = requests.post(
            BASE_URL + "/api/v1/private/order/submit",
            json=params,
            headers=headers,
            timeout=15
        )
    except requests.RequestException as e:
        return jsonify({
            "step": "request_to_mexc_failed",
            "details": str(e)
        }), 500

    try:
        mexc_json = response.json()
    except ValueError:
        mexc_json = None

    return jsonify({
        "step": "mexc_response",
        "tradingview_data": data,
        "sent_params": params,
        "mexc_status_code": response.status_code,
        "mexc_json": mexc_json,
        "mexc_text": response.text
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
