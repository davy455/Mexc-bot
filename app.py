from flask import Flask, request, jsonify
import requests
import time
import hmac
import hashlib

app = Flask(__name__)

API_KEY = "mx0vgl74MjSCVgG712"
API_SECRET = "15d9c38c65fd4062afaab277f07ad63d"

BASE_URL = "https://contract.mexc.com"


def sign(params):
    query_string = "&".join([f"{k}={params[k]}" for k in sorted(params)])
    return hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()


@app.route("/")
def home():
    return "Bot running 🚀"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    print("TradingView:", data)

    side = data.get("side")

    if side == "buy":
        side_value = 1
    elif side == "sell":
        side_value = 2
    else:
        return jsonify({"error": "invalid side"}), 400

    params = {
        "symbol": "XAUT_USDT",
        "price": 0,
        "vol": 1,
        "side": side_value,
        "type": 5,  # ✅ MARKET ORDER (BELANGRIJK)
        "openType": 1,
        "leverage": 5,
        "externalOid": str(int(time.time() * 1000)),
        "timestamp": int(time.time() * 1000)
    }

    params["sign"] = sign(params)

    headers = {
        "ApiKey": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        BASE_URL + "/api/v1/private/order/submit",
        json=params,
        headers=headers
    )

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

    return jsonify({
        "status": response.status_code,
        "response": response.text
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
