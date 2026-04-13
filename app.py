from flask import Flask, request, jsonify
import os
import stripe
from dotenv import load_dotenv

# Load env
load_dotenv()


app = Flask(__name__)

# Stripe config
stripe.api_key = os.getenv("MY_STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET")



@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "running"}), 200



@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    from project_functions import handle_stripe_event
    handle_stripe_event(event)

    return jsonify({"status": "success"}), 200



if __name__ == '__main__':
    app.run(port=5121, debug=True)