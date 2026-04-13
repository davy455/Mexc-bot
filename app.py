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

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        return jsonify({
            "status": response.status_code,
            "response": response.text
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500
