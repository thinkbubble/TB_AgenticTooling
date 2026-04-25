from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import easypost

from team_easypost.project_functions import create_shipment, track_shipment

load_dotenv()

app = Flask(__name__)

EASYPOST_API_KEY = os.getenv("EASYPOST_API_KEY")
API_SECRET = os.getenv("API_SECRET", "test123")

client = easypost.EasyPostClient(EASYPOST_API_KEY)


def verify_token():
    auth_header = request.headers.get("Authorization")
    expected_token = f"Bearer {API_SECRET}"
    return auth_header == expected_token


def serialize_rate(rate):
    if not rate:
        return None

    return {
        "id": getattr(rate, "id", None),
        "carrier": getattr(rate, "carrier", None),
        "service": getattr(rate, "service", None),
        "rate": getattr(rate, "rate", None),
        "currency": getattr(rate, "currency", None),
        "delivery_days": getattr(rate, "delivery_days", None),
        "delivery_date": str(getattr(rate, "delivery_date", None)) if getattr(rate, "delivery_date", None) else None,
        "delivery_date_guaranteed": getattr(rate, "delivery_date_guaranteed", None),
    }


def serialize_address(address):
    if not address:
        return None

    return {
        "id": getattr(address, "id", None),
        "name": getattr(address, "name", None),
        "company": getattr(address, "company", None),
        "street1": getattr(address, "street1", None),
        "street2": getattr(address, "street2", None),
        "city": getattr(address, "city", None),
        "state": getattr(address, "state", None),
        "zip": getattr(address, "zip", None),
        "country": getattr(address, "country", None),
        "phone": getattr(address, "phone", None),
        "email": getattr(address, "email", None),
        "residential": getattr(address, "residential", None),
    }


def serialize_postage_label(postage_label):
    if not postage_label:
        return None

    return {
        "label_url": getattr(postage_label, "label_url", None),
        "label_pdf_url": getattr(postage_label, "label_pdf_url", None),
        "label_zpl_url": getattr(postage_label, "label_zpl_url", None),
        "label_epl2_url": getattr(postage_label, "label_epl2_url", None),
        "label_file_type": getattr(postage_label, "label_file_type", None),
    }


def serialize_tracking_detail(detail):
    return {
        "message": getattr(detail, "message", None),
        "status": getattr(detail, "status", None),
        "datetime": str(getattr(detail, "datetime", None)) if getattr(detail, "datetime", None) else None,
        "source": getattr(detail, "source", None),
        "tracking_location": getattr(detail, "tracking_location", None),
    }


def serialize_tracker(tracker):
    if not tracker:
        return None

    tracking_details = []
    for detail in getattr(tracker, "tracking_details", []) or []:
        tracking_details.append(serialize_tracking_detail(detail))

    return {
        "id": getattr(tracker, "id", None),
        "tracking_code": getattr(tracker, "tracking_code", None),
        "carrier": getattr(tracker, "carrier", None),
        "status": getattr(tracker, "status", None),
        "public_url": getattr(tracker, "public_url", None),
        "est_delivery_date": str(getattr(tracker, "est_delivery_date", None)) if getattr(tracker, "est_delivery_date", None) else None,
        "shipment_id": getattr(tracker, "shipment_id", None),
        "tracking_details": tracking_details,
    }


def serialize_shipment(shipment):
    if not shipment:
        return None

    rates = []
    for rate in getattr(shipment, "rates", []) or []:
        rates.append(serialize_rate(rate))

    return {
        "shipment_id": getattr(shipment, "id", None),
        "status": getattr(shipment, "status", None),
        "tracking_code": getattr(shipment, "tracking_code", None),
        "reference": getattr(shipment, "reference", None),
        "from_address": serialize_address(getattr(shipment, "from_address", None)),
        "to_address": serialize_address(getattr(shipment, "to_address", None)),
        "selected_rate": serialize_rate(getattr(shipment, "selected_rate", None)),
        "postage_label": serialize_postage_label(getattr(shipment, "postage_label", None)),
        "rates": rates,
    }


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "EasyPost Test API is running"
    }), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "running",
        "environment": "test_mode_only"
    }), 200


@app.route("/shipments/create", methods=["POST"])
def api_create_shipment():
    if not verify_token():
        return jsonify({
            "success": False,
            "error": "Unauthorized"
        }), 401

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must be JSON"
            }), 400

        from_address = data.get("from_address")
        to_address = data.get("to_address")
        parcel = data.get("parcel")
        customs_info = data.get("customs_info")
        verify_addresses = data.get("verify_addresses", False)

        if not from_address or not to_address or not parcel:
            return jsonify({
                "success": False,
                "error": "from_address, to_address, and parcel are required"
            }), 400

        shipment = create_shipment(
            from_address=from_address,
            to_address=to_address,
            parcel=parcel,
            customs_info=customs_info,
            verify_addresses=verify_addresses
        )

        return jsonify({
            "success": True,
            "message": "Shipment created successfully in test mode",
            "shipment": serialize_shipment(shipment)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route("/shipments/buy", methods=["POST"])
def api_buy_shipment():
    if not verify_token():
        return jsonify({
            "success": False,
            "error": "Unauthorized"
        }), 401

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must be JSON"
            }), 400

        shipment_id = data.get("shipment_id")
        rate_id = data.get("rate_id")

        if not shipment_id or not rate_id:
            return jsonify({
                "success": False,
                "error": "shipment_id and rate_id are required"
            }), 400

        shipment = client.shipment.retrieve(shipment_id)

        bought_shipment = client.shipment.buy(
            shipment.id,
            rate={"id": rate_id}
        )

        return jsonify({
            "success": True,
            "message": "Shipment purchased successfully",
            "shipment_id": getattr(bought_shipment, "id", None),
            "status": getattr(bought_shipment, "status", None),
            "tracking_code": getattr(bought_shipment, "tracking_code", None),
            "selected_rate": serialize_rate(getattr(bought_shipment, "selected_rate", None)),
            "label_url": getattr(getattr(bought_shipment, "postage_label", None), "label_url", None),
            "postage_label": serialize_postage_label(getattr(bought_shipment, "postage_label", None))
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route("/track", methods=["POST"])
def api_create_tracker():
    if not verify_token():
        return jsonify({
            "success": False,
            "error": "Unauthorized"
        }), 401

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must be JSON"
            }), 400

        tracking_code = data.get("tracking_code")
        carrier = data.get("carrier")

        if not tracking_code:
            return jsonify({
                "success": False,
                "error": "tracking_code is required"
            }), 400

        tracker = track_shipment(
            tracking_code=tracking_code,
            carrier=carrier
        )

        return jsonify(tracker), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route("/webhooks/easypost", methods=["POST"])
def easypost_webhook():
    try:
        data = request.get_json()

        print("\n=== EASYPOST WEBHOOK RECEIVED ===")
        print(data)

        return jsonify({
            "success": True,
            "message": "Webhook received"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)