from flask import Flask, request, jsonify
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY not found in .env")


@app.route("/")
def home():
    return "Server running"


@app.route("/create-checkout-session", methods=["POST"])
def create_checkout():
    try:
        data = request.json
        print("Incoming:", data)  # DEBUG

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": data.get("product_name")
                    },
                    "unit_amount": data.get("amount")
                },
                "quantity": 1
            }],
            mode="payment",
            success_url="http://localhost:5000/success",
            cancel_url="http://localhost:5000/cancel"
        )

        print("Stripe URL:", session.url)  # DEBUG

        return jsonify({"url": session.url})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/success")
def success():
    return "Payment Success"


@app.route("/cancel")
def cancel():
    return "Payment Cancelled"


if __name__ == "__main__":
    app.run(port=5000, debug=True)