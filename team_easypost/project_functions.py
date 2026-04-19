import os
import sys
import logging
from typing import Any, Dict, Optional, List

import easypost
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from helper import *  # noqa: F401,F403

load_dotenv()

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Config
# -------------------------------------------------------------------
EASYPOST_API_KEY_ENV = "EASYPOST_API_KEY"


# -------------------------------------------------------------------
# Client
# -------------------------------------------------------------------
def get_client() -> easypost.EasyPostClient:
    """
    Create and return an EasyPost client using the API key from .env.

    Returns:
        EasyPostClient: Authenticated EasyPost client.

    Raises:
        ValueError: If API key is missing.
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
    Return True if the shipment crosses country borders.

    Args:
        from_address: Sender address dictionary.
        to_address: Receiver address dictionary.

    Returns:
        bool: True if countries differ, else False.

    Raises:
        ValueError: If either address is missing country.
    """
    from_country = str(from_address.get("country", "")).strip().upper()
    to_country = str(to_address.get("country", "")).strip().upper()

    if not from_country or not to_country:
        raise ValueError("Both from_address and to_address must include a country code.")

    return from_country != to_country


def validate_required_fields(data: Dict[str, Any], required_fields: List[str], object_name: str) -> None:
    """
    Validate required fields in a dictionary.

    Args:
        data: Input dictionary.
        required_fields: List of required keys.
        object_name: Logical object name for error messages.

    Raises:
        ValueError: If any required field is missing or empty.
    """
    for field in required_fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"{object_name} must include '{field}'.")


def validate_parcel(parcel: Dict[str, Any]) -> None:
    """
    Validate parcel dimensions and weight.

    Args:
        parcel: Parcel dictionary containing length, width, height, weight.

    Raises:
        ValueError: If parcel fields are missing or invalid.
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
    Validate minimum required address fields before EasyPost verification.

    Args:
        address: Address dictionary.

    Raises:
        ValueError: If required fields are missing.
    """
    required_fields = ["street1", "city", "state", "zip", "country"]
    validate_required_fields(address, required_fields, "address")


def validate_address(
    address: Dict[str, Any],
    strict: bool = True,
    verify_carrier: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create and verify an address in EasyPost.

    strict=True:
        EasyPost raises an error if verification fails.

    strict=False:
        EasyPost returns an address object with verification results.

    Args:
        address: Address dictionary.
        strict: Whether verification should fail hard.
        verify_carrier: Optional carrier-specific verification.

    Returns:
        Dict[str, Any]: Structured verified address.

    Raises:
        ValueError: If address input is incomplete.
        RuntimeError: If EasyPost verification fails.
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

    Args:
        items: List of customs item dictionaries.
        customs_signer: Name of customs signer.
        contents_type: Type of shipment contents.
        non_delivery_option: Action if shipment is undeliverable.
        restriction_type: Restriction type.
        eel_pfc: Optional export code.

    Returns:
        Dict[str, Any]: Dictionary containing customs_info_id.

    Raises:
        ValueError: If customs input is invalid.
        RuntimeError: If customs creation fails.
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
) -> Dict[str, Any]:
    """
    Create an EasyPost shipment with automatic international validation logic.

    Args:
        from_address: Sender address dictionary.
        to_address: Receiver address dictionary.
        parcel: Parcel dictionary.
        customs_info: Optional customs info dictionary like {"customs_info_id": "..."}.
        verify_addresses: If True, validates addresses before shipment creation.

    Returns:
        Dict[str, Any]: Structured shipment dictionary.

    Raises:
        ValueError: If required input is missing or invalid.
        RuntimeError: If shipment creation fails.
    """
    if not from_address:
        raise ValueError("from_address is required.")
    if not to_address:
        raise ValueError("to_address is required.")
    if not parcel:
        raise ValueError("parcel is required.")

    validate_parcel(parcel)

    shipment_from_address = from_address
    shipment_to_address = to_address

    if verify_addresses:
        shipment_from_address = validate_address(from_address)
        shipment_to_address = validate_address(to_address)

    international = is_international(shipment_from_address, shipment_to_address)

    if international and not customs_info:
        raise ValueError("customs_info is required for international shipments.")

    client = get_client()

    shipment_data = {
        "from_address": from_address,
        "to_address": to_address,
        "parcel": parcel,
    }

    if international and customs_info:
        customs_info_id = customs_info.get("customs_info_id") or customs_info.get("id")
        if not customs_info_id:
            raise ValueError("customs_info must include 'customs_info_id' or 'id'.")
        shipment_data["customs_info"] = {"id": customs_info_id}

    try:
        shipment = client.shipment.create(**shipment_data)
        logger.info("Shipment created successfully.")
        return shipment_to_dict(shipment)
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Shipment creation failed: {exc}") from exc


def get_available_rates(shipment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract and normalize shipment rates.

    Args:
        shipment: Structured shipment dictionary.

    Returns:
        List[Dict[str, Any]]: List of normalized rate dictionaries.
    """
    rates = shipment.get("rates", [])
    normalized_rates = []

    for rate in rates:
        normalized_rates.append(
            {
                "id": rate.get("id"),
                "carrier": rate.get("carrier"),
                "service": rate.get("service"),
                "rate": safe_float(rate.get("rate")),
                "currency": rate.get("currency"),
                "delivery_days": rate.get("delivery_days"),
            }
        )

    return normalized_rates


def select_best_rate(
    shipment: Dict[str, Any],
    preferred_carriers: Optional[List[str]] = None,
    preferred_service: Optional[str] = None,
    max_delivery_days: Optional[int] = None,
    cheapest: bool = True,
) -> Dict[str, Any]:
    """
    Select the best matching shipment rate.

    Args:
        shipment: Structured shipment dictionary.
        preferred_carriers: Optional allowed carriers.
        preferred_service: Optional preferred service type.
        max_delivery_days: Optional max delivery time.
        cheapest: If True, pick cheapest among matches.

    Returns:
        Dict[str, Any]: Selected rate dictionary.

    Raises:
        ValueError: If shipment has no rates or no rates match filters.
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
        best_rate = min(filtered_rates, key=lambda r: r["rate"])
    else:
        best_rate = filtered_rates[0]

    return best_rate


# -------------------------------------------------------------------
# Buy Label / Insurance / Tracking
# -------------------------------------------------------------------
def buy_label(
    shipment_id: str,
    rate: Dict[str, Any],
    insurance_amount: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Buy a shipping label for a shipment.

    Args:
        shipment_id: EasyPost shipment ID.
        rate: Selected rate dictionary.
        insurance_amount: Optional insurance amount string, like "100.00".

    Returns:
        Dict[str, Any]: Structured shipment dictionary after label purchase.

    Raises:
        ValueError: If shipment_id or rate is missing.
        RuntimeError: If label purchase fails.
    """
    if not shipment_id:
        raise ValueError("shipment_id is required.")
    if not rate:
        raise ValueError("rate is required.")

    rate_id = rate.get("id")
    if not rate_id:
        raise ValueError("Selected rate must include 'id'.")

    client = get_client()
    rate_payload = {"id": rate_id}

    try:
        if insurance_amount:
            bought_shipment = client.shipment.buy(
                shipment_id,
                rate=rate_payload,
                insurance=insurance_amount,
            )
        else:
            bought_shipment = client.shipment.buy(
                shipment_id,
                rate=rate_payload,
            )

        logger.info("Label purchased successfully.")
        return shipment_to_dict(bought_shipment)

    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Label purchase failed: {exc}") from exc


def insure_existing_shipment(shipment_id: str, insurance_amount: str) -> Dict[str, Any]:
    """
    Add insurance to an already created shipment.

    Args:
        shipment_id: EasyPost shipment ID.
        insurance_amount: Insurance amount string.

    Returns:
        Dict[str, Any]: Structured shipment dictionary.

    Raises:
        ValueError: If shipment_id or insurance_amount is missing.
        RuntimeError: If insurance update fails.
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
        return shipment_to_dict(insured_shipment)
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Shipment insurance failed: {exc}") from exc


def track_shipment(tracking_code: str, carrier: Optional[str] = None) -> Dict[str, Any]:
    """
    Register a tracker in EasyPost using a tracking code.

    Args:
        tracking_code: Shipment tracking code.
        carrier: Optional carrier name.

    Returns:
        Dict[str, Any]: Structured tracker dictionary.

    Raises:
        ValueError: If tracking_code is missing.
        RuntimeError: If tracking setup fails.
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
        return tracker_to_dict(tracker)

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

    Args:
        value: Any incoming value.

    Returns:
        Optional[float]: Float value or None.
    """
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def address_to_dict(address_obj: Any) -> Dict[str, Any]:
    """
    Convert an EasyPost address object into a clean dictionary.
    """
    if isinstance(address_obj, dict):
        return {
            "id": address_obj.get("id"),
            "name": address_obj.get("name"),
            "company": address_obj.get("company"),
            "street1": address_obj.get("street1"),
            "street2": address_obj.get("street2"),
            "city": address_obj.get("city"),
            "state": address_obj.get("state"),
            "zip": address_obj.get("zip"),
            "country": address_obj.get("country"),
            "residential": address_obj.get("residential"),
            "verifications": address_obj.get("verifications"),
        }

    return {
        "id": getattr(address_obj, "id", None),
        "name": getattr(address_obj, "name", None),
        "company": getattr(address_obj, "company", None),
        "street1": getattr(address_obj, "street1", None),
        "street2": getattr(address_obj, "street2", None),
        "city": getattr(address_obj, "city", None),
        "state": getattr(address_obj, "state", None),
        "zip": getattr(address_obj, "zip", None),
        "country": getattr(address_obj, "country", None),
        "residential": getattr(address_obj, "residential", None),
        "verifications": getattr(address_obj, "verifications", None),
    }


def rate_to_dict(rate: Any) -> Dict[str, Any]:
    """
    Convert a rate object into a clean dictionary.
    """
    if isinstance(rate, dict):
        return {
            "id": rate.get("id"),
            "carrier": rate.get("carrier"),
            "service": rate.get("service"),
            "rate": safe_float(rate.get("rate")),
            "currency": rate.get("currency"),
            "delivery_days": rate.get("delivery_days"),
        }

    return {
        "id": getattr(rate, "id", None),
        "carrier": getattr(rate, "carrier", None),
        "service": getattr(rate, "service", None),
        "rate": safe_float(getattr(rate, "rate", None)),
        "currency": getattr(rate, "currency", None),
        "delivery_days": getattr(rate, "delivery_days", None),
    }


def shipment_to_dict(shipment: Any) -> Dict[str, Any]:
    """
    Convert a shipment object into a structured dictionary.
    """
    if isinstance(shipment, dict):
        return {
            "shipment_id": shipment.get("shipment_id") or shipment.get("id"),
            "status": shipment.get("status"),
            "tracking_code": shipment.get("tracking_code"),
            "label_url": shipment.get("label_url"),
            "from_address": shipment.get("from_address"),
            "to_address": shipment.get("to_address"),
            "selected_rate": shipment.get("selected_rate"),
            "rates": shipment.get("rates", []),
        }

    from_address_obj = getattr(shipment, "from_address", None)
    to_address_obj = getattr(shipment, "to_address", None)
    selected_rate_obj = getattr(shipment, "selected_rate", None)
    rates_obj = getattr(shipment, "rates", []) or []
    postage_label = getattr(shipment, "postage_label", None)

    return {
        "shipment_id": getattr(shipment, "id", None),
        "status": getattr(shipment, "status", None),
        "tracking_code": getattr(shipment, "tracking_code", None),
        "label_url": getattr(postage_label, "label_url", None) if postage_label else None,
        "from_address": address_to_dict(from_address_obj) if from_address_obj else None,
        "to_address": address_to_dict(to_address_obj) if to_address_obj else None,
        "selected_rate": rate_to_dict(selected_rate_obj) if selected_rate_obj else None,
        "rates": [rate_to_dict(rate) for rate in rates_obj],
    }


def tracker_to_dict(tracker: Any) -> Dict[str, Any]:
    """
    Convert a tracker object into a structured dictionary.
    """
    if isinstance(tracker, dict):
        return {
            "tracker_id": tracker.get("tracker_id") or tracker.get("id"),
            "tracking_code": tracker.get("tracking_code"),
            "status": tracker.get("status"),
            "carrier": tracker.get("carrier"),
            "public_url": tracker.get("public_url"),
        }

    return {
        "tracker_id": getattr(tracker, "id", None),
        "tracking_code": getattr(tracker, "tracking_code", None),
        "status": getattr(tracker, "status", None),
        "carrier": getattr(tracker, "carrier", None),
        "public_url": getattr(tracker, "public_url", None),
    }


# -------------------------------------------------------------------
# Print Helper
# -------------------------------------------------------------------
def print_shipment_details(shipment: Dict[str, Any]) -> None:
    """
    Print shipment details in a readable and safe way.

    Args:
        shipment: Structured shipment dictionary.
    """
    print("\nShipment Details:")
    print(f"Shipment ID   : {shipment.get('shipment_id')}")
    print(f"Status        : {shipment.get('status')}")
    print(f"Tracking Code : {shipment.get('tracking_code') or 'Not available'}")
    print(f"Label URL     : {shipment.get('label_url') or 'Not available'}")

    selected_rate = shipment.get("selected_rate")
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
) -> Dict[str, Any]:
    """
    End-to-end shipment workflow:
    - validate parcel
    - detect international shipment
    - create customs info if needed
    - create shipment
    - select best rate
    - buy label
    - optionally insure

    Args:
        from_address: Sender address.
        to_address: Receiver address.
        parcel: Parcel details.
        customs_items: Optional customs items for international shipment.
        customs_signer: Required for international customs creation.
        insurance_amount: Optional insurance amount.
        verify_addresses: Whether to verify addresses before shipment.
        preferred_carriers: Optional allowed carriers.
        max_delivery_days: Optional delivery limit.
        preferred_service: Optional exact service name.

    Returns:
        Dict[str, Any]: Final shipment dictionary after purchase.

    Raises:
        ValueError: If required inputs are invalid.
        RuntimeError: If any EasyPost step fails.
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
        shipment_id=shipment["shipment_id"],
        rate=best_rate,
        insurance_amount=insurance_amount,
    )

    return purchased_shipment