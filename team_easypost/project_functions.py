import os
import logging
from typing import Any, Dict, Optional, List

import easypost
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Config
# -----------------------------------------------------------------
EASYPOST_API_KEY_ENV = "EASYPOST_API_KEY"


# -------------------------------------------------------------------
# Client
# -------------------------------------------------------------------
def get_client() -> easypost.EasyPostClient:
    """
    Create and return an EasyPost client using the API key from .env.
    """
    api_key = os.getenv(EASYPOST_API_KEY_ENV)
    if not api_key:
        raise ValueError(f"{EASYPOST_API_KEY_ENV} not found in .env file")
    return easypost.EasyPostClient(api_key)


# -------------------------------------------------------------------
# Validation Helpers
# -------------------------------------------------------------------
def is_international(from_address: Dict[str, Any], to_address: Dict[str, Any]) -> bool:
    """
    Return True if shipment crosses country borders.
    """
    from_country = str(from_address.get("country", "")).strip().upper()
    to_country = str(to_address.get("country", "")).strip().upper()

    if not from_country or not to_country:
        raise ValueError("Both from_address and to_address must include a country code.")

    return from_country != to_country


def validate_required_fields(data: Dict[str, Any], required_fields: List[str], object_name: str) -> None:
    """
    Validate required fields in a dictionary.
    """
    for field in required_fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"{object_name} must include '{field}'.")


def validate_parcel(parcel: Dict[str, Any]) -> None:
    """
    Validate parcel dimensions and weight.
    """
    required_fields = ["length", "width", "height", "weight"]
    validate_required_fields(parcel, required_fields, "parcel")

    for field in required_fields:
        try:
            numeric_value = float(parcel[field])
            if numeric_value <= 0:
                raise ValueError
        except (TypeError, ValueError):
            raise ValueError(f"parcel '{field}' must be a number greater than 0.")


def validate_address_input(address: Dict[str, Any]) -> None:
    """
    Validate minimum required address fields.
    """
    required_fields = ["street1", "city", "state", "zip", "country"]
    validate_required_fields(address, required_fields, "address")


def validate_address(
    address: Dict[str, Any],
    strict: bool = True,
    verify_carrier: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create and verify an address in EasyPost, returning a clean dictionary.
    """
    validate_address_input(address)
    client = get_client()
    payload = dict(address)

    try:
        if strict:
            if verify_carrier:
                verified_address = client.address.create(
                    **payload,
                    verify_strict=True,
                    verify_carrier=verify_carrier,
                )
            else:
                verified_address = client.address.create(
                    **payload,
                    verify_strict=True,
                )
        else:
            if verify_carrier:
                verified_address = client.address.create(
                    **payload,
                    verify=True,
                    verify_carrier=verify_carrier,
                )
            else:
                verified_address = client.address.create(
                    **payload,
                    verify=True,
                )

        logger.info("Address validated successfully.")
        return address_to_dict(verified_address)

    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Address verification failed: {exc}") from exc


# -------------------------------------------------------------------
# Customs
# -------------------------------------------------------------------
def create_customs_info(
    items: List[Dict[str, Any]],
    customs_signer: str,
    contents_type: str = "merchandise",
    non_delivery_option: str = "return",
    restriction_type: str = "none",
    eel_pfc: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create customs info for international shipments.
    Returns {"customs_info_id": "..."}.
    """
    if not items:
        raise ValueError("At least one customs item is required for international shipments.")

    if not customs_signer or not str(customs_signer).strip():
        raise ValueError("customs_signer is required.")

    client = get_client()
    customs_items = []

    try:
        for item in items:
            validate_required_fields(
                item,
                ["description", "quantity", "value", "weight", "origin_country"],
                "customs item",
            )

            customs_item_payload = {
                "description": item["description"],
                "quantity": item["quantity"],
                "value": item["value"],
                "weight": item["weight"],
                "origin_country": item["origin_country"],
            }

            if item.get("hs_tariff_number"):
                customs_item_payload["hs_tariff_number"] = item["hs_tariff_number"]

            customs_item = client.customs_item.create(**customs_item_payload)
            customs_items.append({"id": customs_item.id})

        customs_info_payload = {
            "customs_certify": True,
            "customs_signer": customs_signer,
            "contents_type": contents_type,
            "non_delivery_option": non_delivery_option,
            "restriction_type": restriction_type,
            "customs_items": customs_items,
        }

        if eel_pfc:
            customs_info_payload["eel_pfc"] = eel_pfc

        customs_info = client.customs_info.create(**customs_info_payload)
        logger.info("Customs info created successfully.")
        return {"customs_info_id": customs_info.id}

    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Customs creation failed: {exc}") from exc


# -------------------------------------------------------------------
# Shipment / Rate Selection
# -------------------------------------------------------------------
def create_shipment(
    from_address: Dict[str, Any],
    to_address: Dict[str, Any],
    parcel: Dict[str, Any],
    customs_info: Optional[Dict[str, Any]] = None,
    verify_addresses: bool = False,
):
    """
    Create an EasyPost shipment and return the RAW EasyPost shipment object.
    This matches your current app.py.
    """
    if not from_address:
        raise ValueError("from_address is required.")
    if not to_address:
        raise ValueError("to_address is required.")
    if not parcel:
        raise ValueError("parcel is required.")

    validate_address_input(from_address)
    validate_address_input(to_address)
    validate_parcel(parcel)

    shipment_from_address = from_address
    shipment_to_address = to_address

    if verify_addresses:
        shipment_from_address = validate_address(from_address)
        shipment_to_address = validate_address(to_address)

    international = is_international(shipment_from_address, shipment_to_address)

    client = get_client()

    shipment_data = {
        "from_address": shipment_from_address,
        "to_address": shipment_to_address,
        "parcel": parcel,
    }

    if international:
        if not customs_info:
            raise ValueError("customs_info is required for international shipments.")

        customs_info_id = customs_info.get("customs_info_id") or customs_info.get("id")
        if not customs_info_id:
            raise ValueError("customs_info must include 'customs_info_id' or 'id'.")

        shipment_data["customs_info"] = {"id": customs_info_id}

    try:
        shipment = client.shipment.create(**shipment_data)
        logger.info("Shipment created successfully.")
        return shipment

    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Shipment creation failed: {exc}") from exc


def get_available_rates(shipment: Any) -> List[Dict[str, Any]]:
    """
    Extract and normalize shipment rates from either a dict or raw EasyPost object.
    """
    if isinstance(shipment, dict):
        rates = shipment.get("rates", []) or []
    else:
        rates = getattr(shipment, "rates", []) or []

    normalized_rates = []

    for rate in rates:
        normalized_rates.append(
            {
                "id": _get_value(rate, "id"),
                "carrier": _get_value(rate, "carrier"),
                "service": _get_value(rate, "service"),
                "rate": safe_float(_get_value(rate, "rate")),
                "currency": _get_value(rate, "currency"),
                "delivery_days": _get_value(rate, "delivery_days"),
            }
        )

    return normalized_rates


def select_best_rate(
    shipment: Any,
    preferred_carriers: Optional[List[str]] = None,
    preferred_service: Optional[str] = None,
    max_delivery_days: Optional[int] = None,
    cheapest: bool = True,
) -> Dict[str, Any]:
    """
    Select the best matching rate from a shipment.
    Works with raw EasyPost shipment object or dict.
    """
    rates = get_available_rates(shipment)

    if not rates:
        raise ValueError("No shipment rates available.")

    filtered_rates = rates

    if preferred_carriers:
        carrier_set = {carrier.strip().lower() for carrier in preferred_carriers}
        filtered_rates = [
            rate
            for rate in filtered_rates
            if rate.get("carrier") and rate["carrier"].strip().lower() in carrier_set
        ]

    if preferred_service:
        preferred_service_lower = preferred_service.strip().lower()
        filtered_rates = [
            rate
            for rate in filtered_rates
            if rate.get("service") and rate["service"].strip().lower() == preferred_service_lower
        ]

    if max_delivery_days is not None:
        filtered_rates = [
            rate
            for rate in filtered_rates
            if rate.get("delivery_days") is not None and rate["delivery_days"] <= max_delivery_days
        ]

    if not filtered_rates:
        raise ValueError("No rates matched the given selection criteria.")

    filtered_rates = [rate for rate in filtered_rates if rate.get("rate") is not None]

    if not filtered_rates:
        raise ValueError("Matched rates exist, but none have a valid numeric price.")

    if cheapest:
        return min(filtered_rates, key=lambda r: r["rate"])

    return filtered_rates[0]


# -------------------------------------------------------------------
# Buy Label / Insurance / Tracking
# -------------------------------------------------------------------
def buy_label(
    shipment_id: str,
    rate: Dict[str, Any],
    insurance_amount: Optional[str] = None,
):
    """
    Buy a shipping label and return the RAW EasyPost shipment object.
    """
    if not shipment_id:
        raise ValueError("shipment_id is required.")
    if not rate:
        raise ValueError("rate is required.")

    rate_id = rate.get("id")
    if not rate_id:
        raise ValueError("Selected rate must include 'id'.")

    client = get_client()

    try:
        if insurance_amount:
            bought_shipment = client.shipment.buy(
                shipment_id,
                rate={"id": rate_id},
                insurance=insurance_amount,
            )
        else:
            bought_shipment = client.shipment.buy(
                shipment_id,
                rate={"id": rate_id},
            )

        logger.info("Label purchased successfully.")
        return bought_shipment

    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Label purchase failed: {exc}") from exc


def insure_existing_shipment(shipment_id: str, insurance_amount: str):
    """
    Add insurance to an already created shipment and return raw object.
    """
    if not shipment_id:
        raise ValueError("shipment_id is required.")
    if not insurance_amount:
        raise ValueError("insurance_amount is required.")

    client = get_client()

    try:
        insured_shipment = client.shipment.insure(
            shipment_id,
            amount=insurance_amount,
        )
        logger.info("Shipment insured successfully.")
        return insured_shipment

    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Shipment insurance failed: {exc}") from exc


def track_shipment(tracking_code: str, carrier: Optional[str] = None):
    """
    Register a tracker and return clean JSON response.
    """
    if not tracking_code:
        raise ValueError("tracking_code is required.")

    client = get_client()

    try:
        if carrier:
            tracker = client.tracker.create(
                tracking_code=tracking_code,
                carrier=carrier,
            )
        else:
            tracker = client.tracker.create(
                tracking_code=tracking_code,
            )

        logger.info("Tracker created successfully.")

        return {
            "tracking_code": tracker.tracking_code,
            "status": tracker.status,
            "carrier": tracker.carrier,
            "est_delivery_date": tracker.est_delivery_date,
            "history": [
                {
                    "status": detail.status,
                    "message": detail.message,
                    "datetime": detail.datetime
                }
                for detail in tracker.tracking_details
            ]
        }

    except ValueError:
        raise

    except Exception as exc:
        raise RuntimeError(f"Tracking setup failed: {exc}") from exc

# -------------------------------------------------------------------
# Structured Output Helpers
# -------------------------------------------------------------------
def safe_float(value: Any) -> Optional[float]:
    """
    Convert a value to float safely.
    """
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _get_value(obj: Any, key: str) -> Any:
    """
    Safely get a value from either dict or object.
    """
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def address_to_dict(address_obj: Any) -> Dict[str, Any]:
    """
    Convert an EasyPost address object into a clean dictionary.
    """
    def serialize_verifications(verifications):
        if verifications is None:
            return None
        if isinstance(verifications, dict):
            return verifications
        if hasattr(verifications, "__dict__"):
            return {
                key: value
                for key, value in verifications.__dict__.items()
                if not key.startswith("_")
            }
        return str(verifications)

    return {
        "id": _get_value(address_obj, "id"),
        "name": _get_value(address_obj, "name"),
        "company": _get_value(address_obj, "company"),
        "street1": _get_value(address_obj, "street1"),
        "street2": _get_value(address_obj, "street2"),
        "city": _get_value(address_obj, "city"),
        "state": _get_value(address_obj, "state"),
        "zip": _get_value(address_obj, "zip"),
        "country": _get_value(address_obj, "country"),
        "residential": _get_value(address_obj, "residential"),
        "verifications": serialize_verifications(_get_value(address_obj, "verifications")),
    }


def rate_to_dict(rate: Any) -> Dict[str, Any]:
    """
    Convert a rate object into a clean dictionary.
    """
    return {
        "id": _get_value(rate, "id"),
        "carrier": _get_value(rate, "carrier"),
        "service": _get_value(rate, "service"),
        "rate": safe_float(_get_value(rate, "rate")),
        "currency": _get_value(rate, "currency"),
        "delivery_days": _get_value(rate, "delivery_days"),
    }


def shipment_to_dict(shipment: Any) -> Dict[str, Any]:
    """
    Convert a shipment object into a structured dictionary.
    """
    from_address_obj = _get_value(shipment, "from_address")
    to_address_obj = _get_value(shipment, "to_address")
    selected_rate_obj = _get_value(shipment, "selected_rate")
    rates_obj = _get_value(shipment, "rates") or []
    postage_label = _get_value(shipment, "postage_label")

    return {
        "shipment_id": _get_value(shipment, "shipment_id") or _get_value(shipment, "id"),
        "status": _get_value(shipment, "status"),
        "tracking_code": _get_value(shipment, "tracking_code"),
        "label_url": _get_value(postage_label, "label_url") if postage_label else None,
        "from_address": address_to_dict(from_address_obj) if from_address_obj else None,
        "to_address": address_to_dict(to_address_obj) if to_address_obj else None,
        "selected_rate": rate_to_dict(selected_rate_obj) if selected_rate_obj else None,
        "rates": [rate_to_dict(rate) for rate in rates_obj],
    }


def tracker_to_dict(tracker: Any) -> Dict[str, Any]:
    """
    Convert a tracker object into a structured dictionary.
    """
    return {
        "tracker_id": _get_value(tracker, "tracker_id") or _get_value(tracker, "id"),
        "tracking_code": _get_value(tracker, "tracking_code"),
        "status": _get_value(tracker, "status"),
        "carrier": _get_value(tracker, "carrier"),
        "public_url": _get_value(tracker, "public_url"),
    }


# -------------------------------------------------------------------
# Print Helper
# -------------------------------------------------------------------
def print_shipment_details(shipment: Any) -> None:
    """
    Print shipment details in a readable and safe way.
    """
    shipment_data = shipment_to_dict(shipment)

    print("\nShipment Details:")
    print(f"Shipment ID   : {shipment_data.get('shipment_id')}")
    print(f"Status        : {shipment_data.get('status')}")
    print(f"Tracking Code : {shipment_data.get('tracking_code') or 'Not available'}")
    print(f"Label URL     : {shipment_data.get('label_url') or 'Not available'}")

    selected_rate = shipment_data.get("selected_rate")
    if selected_rate:
        print(
            "Selected Rate : "
            f"{selected_rate.get('carrier')} | "
            f"{selected_rate.get('service')} | "
            f"{selected_rate.get('rate')} {selected_rate.get('currency')} | "
            f"Delivery Days: {selected_rate.get('delivery_days')}"
        )


# -------------------------------------------------------------------
# End-to-End Workflow
# -------------------------------------------------------------------
def process_shipment(
    from_address: Dict[str, Any],
    to_address: Dict[str, Any],
    parcel: Dict[str, Any],
    customs_items: Optional[List[Dict[str, Any]]] = None,
    customs_signer: Optional[str] = None,
    insurance_amount: Optional[str] = None,
    verify_addresses: bool = False,
    preferred_carriers: Optional[List[str]] = None,
    max_delivery_days: Optional[int] = None,
    preferred_service: Optional[str] = None,
):
    """
    End-to-end shipment workflow returning RAW purchased shipment object.
    """
    validate_parcel(parcel)

    international = is_international(from_address, to_address)

    customs_info = None
    if international:
        if not customs_items:
            raise ValueError("customs_items are required for international shipments.")
        if not customs_signer:
            raise ValueError("customs_signer is required for international shipments.")

        customs_info = create_customs_info(
            items=customs_items,
            customs_signer=customs_signer,
        )

    shipment = create_shipment(
        from_address=from_address,
        to_address=to_address,
        parcel=parcel,
        customs_info=customs_info,
        verify_addresses=verify_addresses,
    )

    best_rate = select_best_rate(
        shipment=shipment,
        preferred_carriers=preferred_carriers,
        preferred_service=preferred_service,
        max_delivery_days=max_delivery_days,
        cheapest=True,
    )

    purchased_shipment = buy_label(
        shipment_id=getattr(shipment, "id", None),
        rate=best_rate,
        insurance_amount=insurance_amount,
    )

    return purchased_shipment