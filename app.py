from flask import Flask, request, jsonify
import os
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Stripe configuration
stripe.api_key = os.getenv("MY_STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET")

# =========================
# Health Check Route
# =========================
@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "running"}), 200


# =========================
# Generic Webhook (Optional)
# =========================
@app.route('/webhook/your_service', methods=['POST'])
def webhook():
    try:
        data = request.get_json(silent=True)

        if data is None:
            data = request.data.decode('utf-8')

        print("Received generic webhook:", data)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Error processing webhook:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


# =========================
# Stripe Webhook
# =========================
@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        # Verify webhook signature (IMPORTANT)
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

    except ValueError:
        print("Invalid payload")
        return jsonify({"error": "Invalid payload"}), 400

    except stripe.error.SignatureVerificationError:
        print("Invalid signature")
        return jsonify({"error": "Invalid signature"}), 400

    # Import here to avoid circular imports
    from functions import handle_stripe_event

    # Process event
    handle_stripe_event(event)

    return jsonify({"status": "success"}), 200


# =========================
# Run Server
# =========================
if __name__ == '__main__':
    port = 5121
    print(f" Server running on http://127.0.0.1:{port}")
    app.run(port=port, debug=True)