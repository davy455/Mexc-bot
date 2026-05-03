import base64

OKX_API_KEY = os.environ.get("OKX_API_KEY")
OKX_SECRET = os.environ.get("OKX_SECRET")
OKX_PASSPHRASE = os.environ.get("OKX_PASSPHRASE")

OKX_URL = "https://www.okx.com"

def okx_sign(timestamp, method, request_path, body):
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(
        OKX_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    )
    return base64.b64encode(mac.digest()).decode()


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("DATA:", data, flush=True)

    side = data.get("side")

    if side == "buy":
        okx_side = "buy"
    elif side == "sell":
        okx_side = "sell"
    else:
        return jsonify({"error": "invalid side"}), 400

    body = json.dumps({
        "instId": "BTC-USDT-SWAP",
        "tdMode": "isolated",
        "side": okx_side,
        "ordType": "market",
        "sz": "1"
    })

    timestamp = str(time.time())

    sign = okx_sign(timestamp, "POST", "/api/v5/trade/order", body)

    headers = {
        "OK-ACCESS-KEY": OKX_API_KEY,
        "OK-ACCESS-SIGN": sign,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": OKX_PASSPHRASE,
        "Content-Type": "application/json"
    }

    response = requests.post(
        OKX_URL + "/api/v5/trade/order",
        headers=headers,
        data=body
    )

    print("OKX:", response.text, flush=True)

    return jsonify({"okx": response.text})
