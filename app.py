from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "JOUW_NIEUWE_MEXC_API_KEY"
BASE_URL = "https://contract.mexc.com"


@app.route("/")
def home():
    return "Bot running 🚀"


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        response = requests.get(
            BASE_URL + "/api/v1/private/account/assets",
            headers={
                "ApiKey": API_KEY
            },
            timeout=10
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
