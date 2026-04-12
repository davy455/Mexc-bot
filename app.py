from flask import Flask, request, jsonify
import requests
import time
import hmac
import hashlib

app = Flask(__name__)

API_KEY = "mx0vglUtlgpfcDt94u"
API_SECRET = "7c377ce3bfd943d3a6dd2bd66561d423"

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
        print("No JSON received from TradingView. Raw body:", raw_body)
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
        print("Request to MEXC failed:", str(e))
        return jsonify({
            "error": "Request to MEXC failed",
            "details": str(e)
        }), 500

    print("TradingView data:", data)
    print("MEXC status:", response.status_code)
    print("MEXC response text:", response.text)

    try:
        mexc_json = response.json()
        return jsonify({
            "ok": True,
            "status_code": response.status_code,
            "mexc_response": mexc_json
        }), response.status_code
    except ValueError:
        return jsonify({
            "ok": False,
            "status_code": response.status_code,
            "mexc_response_text": response.text
        }), response.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
