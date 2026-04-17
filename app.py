from flask import Flask, request, jsonify
import requests
import time
import hmac
import hashlib
import json

app = Flask(__name__)

API_KEY = "mx0vglgeq1D2IaxdFg"
API_SECRET = "c448ac4519fc41928aa9ae7e16f786c9"

BASE_URL = "https://api.mexc.com"


def sign(params):
    query_string = "&".join([f"{k}={params[k]}" for k in sorted(params)])
    return hmac.new(
        API_SECRET.encode(),
        query_string.encode(),
        hashlib.sha256
    ).hexdigest()


@app.route("/")
def home():
    return "Bot running 🚀"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if data is None:
        raw = request.get_data(as_text=True)
        print("RAW DATA:", raw, flush=True)
        try:
            data = json.loads(raw)
        except Exception:
            return jsonify({"error": "invalid json", "raw": raw}), 400

    print("TradingView:", data, flush=True)

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
        "type": 5,
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

    try:
        response = requests.post(
            BASE_URL + "/api/v1/private/order/submit",
            json=params,
            headers=headers,
            timeout=15
        )

        print("STATUS:", response.status_code, flush=True)
        print("RESPONSE:", response.text, flush=True)

        return jsonify({
            "status": response.status_code,
            "response": response.text
        }), 200

    except Exception as e:
        print("ERROR:", str(e), flush=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
