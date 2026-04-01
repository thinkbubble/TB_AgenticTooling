from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return {"message": "EasyPost API running with ngrok"}


@app.route("/webhook/easypost", methods=["POST"])
def easypost_webhook():
    data = request.json
    print("\nWEBHOOK RECEIVED")
    print(data)

    return jsonify({
        "status": "success",
        "message": "Webhook received"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)