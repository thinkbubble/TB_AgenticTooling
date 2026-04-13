from flask import Flask, request, jsonify
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse

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

@app.route('/webhook/twilio', methods=['GET', 'POST'])
def webhook():
    sender_number = request.values.get('From', 'Unknown')
    incoming_msg = request.values.get('Body', '')
    print(f"Received a text from {sender_number}: {incoming_msg}")
    response = MessagingResponse()
    response.message("Hello! I received your text message")
    return str(response)

@app.route("/webhook/answercall", methods=['GET', 'POST'])
def webhook_answercall():
    caller_number = request.values.get('From', 'Unknown Number')
    print(f" Incoming call detected from: {caller_number}")
    response = VoiceResponse()
    response.say("Hello! Have a great day")
    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)