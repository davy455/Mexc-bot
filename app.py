from flask import Flask, request, jsonify
import requests
import time
import hmac
import hashlib

app = Flask(__name__)

API_KEY = "mx0vglUtlgpfcDt94u"
API_SECRET = "7c377ce3bfd943d3a6dd2bd66561d423"

BASE_URL = "https://contract.mexc.com"

def sign(params):
    query = "&".join([f"{k}={v}" for k, v in params.items()])
    return hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()

@app.route('/')
def home():
    return "Bot running 🚀"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    side = data.get("side")
    symbol = "AUX_USDT"

    if side == "buy":
        order_side = 1
    elif side == "sell":
        order_side = 2
    else:
        return jsonify({"error": "invalid side"})

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

    r = requests.post(BASE_URL + "/api/v1/private/order/submit", json=params, headers=headers)

    return jsonify(r.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
