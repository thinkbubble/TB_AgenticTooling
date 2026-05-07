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

@app.route('/webhook/message', methods=['GET', 'POST'])
def sms_webhook():
    sender_number = request.values.get('From', 'Unknown')
    incoming_msg = request.values.get('Body', '')
    print(f"[SMS RECEIVED] From {sender_number}: {incoming_msg}")
    response = MessagingResponse()
    response.message("Hello! I received your text message")
    return str(response), 200, {'Content-Type': 'text/xml'}

@app.route("/webhook/answercall", methods=['GET', 'POST'])
def answercall_webhook():
    caller_number = request.values.get('From', 'Unknown Number')
    print(f"[CALL RECEIVED] From: {caller_number}")
    response = VoiceResponse()
    response.say("Hello! Thanks for calling. Have a great day!", voice='alice')
    return str(response), 200, {'Content-Type': 'text/xml'}

@app.route('/receive-email', methods=['GET','POST'])
def receive_email():
    sender = request.form.get('from')
    subject = request.form.get('subject')
    body = request.form.get('text')

    print("From:", sender)
    print("Subject:", subject)
    print("Body:", body)

    return "OK", 200
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)