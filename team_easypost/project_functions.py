import os
import sys
from typing import Any, Dict, Optional, List

import easypost
from dotenv import load_dotenv
# EVERYTHING in helper will be imported

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from helper import *
#from new_helper import name_a_function

load_dotenv()

# Configuration / Client

def get_client() -> easypost.EasyPostClient:
    """
    Create and return an EasyPost client using the API key from .env.
    """
    api_key = os.getenv("EASYPOST_API_KEY")
    if not api_key:
        raise ValueError("EASYPOST_API_KEY not found in .env file")
    return easypost.EasyPostClient(api_key)


# Validation / Basic Helpers

def is_international(from_address: Dict[str, Any], to_address: Dict[str, Any]) -> bool:
    """
    Return True if the shipment crosses country borders.
    """
    from_country = str(from_address.get("country", "")).strip().upper()
    to_country = str(to_address.get("country", "")).strip().upper()

    if not from_country or not to_country:
        raise ValueError("Both from_address and to_address must include a country code.")

    return from_country != to_country


def validate_address(
    address: Dict[str, Any],
    strict: bool = True,
    verify_carrier: Optional[str] = None,
):
    """
    Create and verify an address in EasyPost.

    strict=True:
        EasyPost raises an error if the address cannot be verified.

    strict=False:
        EasyPost returns an address object with verification results.
    """
    client = get_client()

    payload = dict(address)

    try:
        if strict:
            # verify_strict raises an error if verification fails
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
            # verify returns an address object with verification results
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

        return verified_address

    except Exception as exc:
        raise RuntimeError(f"Address verification failed: {exc}") from exc


# Customs

def create_customs_info(
    items: List[Dict[str, Any]],
    customs_signer: str,
    contents_type: str = "merchandise",
    non_delivery_option: str = "return",
    restriction_type: str = "none",
    eel_pfc: Optional[str] = None,
):
    """
    Create dynamic customs info for international shipments.

    Each item in `items` should look like:
    {
        "description": "T-shirt",
        "quantity": 2,
        "value": 25.0,
        "weight": 16.0,
        "hs_tariff_number": "610910",
        "origin_country": "US"
    }
    """
    if not items:
        raise ValueError("At least one customs item is required for international shipments.")

    client = get_client()
    customs_items = []

    try:
        for item in items:
            description = item.get("description")
            quantity = item.get("quantity", 1)
            value = item.get("value")
            weight = item.get("weight")
            origin_country = item.get("origin_country")
            hs_tariff_number = item.get("hs_tariff_number")

            if not description:
                raise ValueError("Each customs item must include 'description'.")
            if value is None:
                raise ValueError("Each customs item must include 'value'.")
            if weight is None:
                raise ValueError("Each customs item must include 'weight'.")
            if not origin_country:
                raise ValueError("Each customs item must include 'origin_country'.")

            customs_item_payload = {
                "description": description,
                "quantity": quantity,
                "value": value,
                "weight": weight,
                "origin_country": origin_country,
            }

            if hs_tariff_number:
                customs_item_payload["hs_tariff_number"] = hs_tariff_number

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
        return {"id": customs_info.id}

    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Customs creation failed: {exc}") from exc


# Shipment / Rate Selection

def create_shipment(
    from_address: Dict[str, Any],
    to_address: Dict[str, Any],
    parcel: Dict[str, Any],
    customs_info: Optional[Dict[str, Any]] = None,
):
    """
    Create an EasyPost shipment.
    """
    client = get_client()

    if not from_address:
        raise ValueError("from_address is required.")
    if not to_address:
        raise ValueError("to_address is required.")
    if not parcel:
        raise ValueError("parcel is required.")

    shipment_data = {
        "from_address": from_address,
        "to_address": to_address,
        "parcel": parcel,
    }

    if customs_info:
        shipment_data["customs_info"] = customs_info

    try:
        shipment = client.shipment.create(**shipment_data)
        return shipment
    except Exception as exc:
        raise RuntimeError(f"Shipment creation failed: {exc}") from exc


def print_rates(shipment) -> None:
    """
    Print all available shipment rates.
    """
    rates = getattr(shipment, "rates", None)
    if not rates:
        print("\nNo rates available for this shipment.")
        return

    print("\nAvailable Rates:")
    print("-" * 80)
    for index, rate in enumerate(rates, start=1):
        print(
            f"{index}. Carrier: {getattr(rate, 'carrier', 'N/A')}, "
            f"Service: {getattr(rate, 'service', 'N/A')}, "
            f"Rate: {getattr(rate, 'rate', 'N/A')} {getattr(rate, 'currency', '')}, "
            f"Delivery Days: {getattr(rate, 'delivery_days', 'N/A')}"
        )


def select_best_rate(
    shipment,
    preferred_carriers: Optional[List[str]] = None,
    preferred_services: Optional[List[str]] = None,
    max_rate: Optional[float] = None,
    max_delivery_days: Optional[int] = None,
):
    """
    Pick the best rate based on user/business rules, not just lowest price.

    Rules:
    1. Start from all rates
    2. Filter by preferred carriers if provided
    3. Filter by preferred services if provided
    4. Filter by max rate if provided
    5. Filter by max delivery days if provided
    6. Choose the lowest-priced remaining rate
    """
    rates = getattr(shipment, "rates", None)
    if not rates:
        raise LookupError("No rates returned for this shipment.")

    filtered_rates = list(rates)

    if preferred_carriers:
        preferred_carriers_normalized = {c.strip().lower() for c in preferred_carriers}
        filtered = [
            r for r in filtered_rates
            if str(getattr(r, "carrier", "")).strip().lower() in preferred_carriers_normalized
        ]
        if filtered:
            filtered_rates = filtered

    if preferred_services:
        preferred_services_normalized = {s.strip().lower() for s in preferred_services}
        filtered = [
            r for r in filtered_rates
            if str(getattr(r, "service", "")).strip().lower() in preferred_services_normalized
        ]
        if filtered:
            filtered_rates = filtered

    if max_rate is not None:
        filtered = [
            r for r in filtered_rates
            if float(getattr(r, "rate", 0)) <= max_rate
        ]
        if filtered:
            filtered_rates = filtered

    if max_delivery_days is not None:
        filtered = []
        for r in filtered_rates:
            delivery_days = getattr(r, "delivery_days", None)
            if delivery_days is not None and int(delivery_days) <= max_delivery_days:
                filtered.append(r)
        if filtered:
            filtered_rates = filtered

    if not filtered_rates:
        raise LookupError("No rates matched the selection criteria.")

    best_rate = min(filtered_rates, key=lambda r: float(getattr(r, "rate", 0)))
    return best_rate


def get_lowest_rate(shipment):
    """
    Keep this helper for compatibility with your old code.
    """
    rates = getattr(shipment, "rates", None)
    if not rates:
        raise LookupError("No rates returned for this shipment.")
    return shipment.lowest_rate()


# Buy Label / Insurance / Tracking

def buy_label(
    shipment_id: str,
    rate,
    insurance_amount: Optional[str] = None,
):
    """
    Buy a shipping label. Optionally add insurance during purchase.
    insurance_amount should be a string like "100.00".
    """
    client = get_client()

    try:
        if insurance_amount:
            bought_shipment = client.shipment.buy(
                shipment_id,
                rate=rate,
                insurance=insurance_amount,
            )
        else:
            bought_shipment = client.shipment.buy(
                shipment_id,
                rate=rate,
            )

        return bought_shipment
    except Exception as exc:
        raise RuntimeError(f"Label purchase failed: {exc}") from exc


def insure_existing_shipment(shipment_id: str, insurance_amount: str):
    """
    Add insurance after purchase, if you prefer a separate insurance step.
    """
    client = get_client()

    try:
        insured_shipment = client.shipment.insure(
            shipment_id,
            amount=insurance_amount,
        )
        return insured_shipment
    except Exception as exc:
        raise RuntimeError(f"Shipment insurance failed: {exc}") from exc


def track_shipment(tracking_code: str, carrier: Optional[str] = None):
    """
    Register a tracker in EasyPost using a tracking code.
    """
    client = get_client()

    if not tracking_code:
        raise ValueError("tracking_code is required.")

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

        return tracker
    except Exception as exc:
        raise RuntimeError(f"Tracking setup failed: {exc}") from exc


# Structured Output Helpers

def address_to_dict(address_obj) -> Dict[str, Any]:
    """
    Convert an EasyPost address object into a clean dictionary.
    """
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


def rate_to_dict(rate) -> Dict[str, Any]:
    """
    Convert a rate object into a clean dictionary.
    """
    return {
        "carrier": getattr(rate, "carrier", None),
        "service": getattr(rate, "service", None),
        "rate": getattr(rate, "rate", None),
        "currency": getattr(rate, "currency", None),
        "delivery_days": getattr(rate, "delivery_days", None),
    }


def shipment_to_dict(shipment) -> Dict[str, Any]:
    """
    Convert a shipment object into a structured dictionary.
    """
    return {
        "shipment_id": getattr(shipment, "id", None),
        "status": getattr(shipment, "status", None),
        "tracking_code": getattr(shipment, "tracking_code", None),
        "label_url": getattr(getattr(shipment, "postage_label", None), "label_url", None),
        "selected_rate": (
            rate_to_dict(getattr(shipment, "selected_rate", None))
            if getattr(shipment, "selected_rate", None)
            else None
        ),
    }


def tracker_to_dict(tracker) -> Dict[str, Any]:
    """
    Convert a tracker object into a structured dictionary.
    """
    return {
        "tracker_id": getattr(tracker, "id", None),
        "tracking_code": getattr(tracker, "tracking_code", None),
        "status": getattr(tracker, "status", None),
        "carrier": getattr(tracker, "carrier", None),
        "public_url": getattr(tracker, "public_url", None),
    }


def print_shipment_details(shipment) -> None:
    """
    Print shipment details in a readable way.
    """
    data = shipment_to_dict(shipment)

    print("\nShipment Details:")
    print("-" * 80)
    print(f"Shipment ID   : {data['shipment_id']}")
    print(f"Status        : {data['status']}")
    print(f"Tracking Code : {data['tracking_code'] or 'Not available'}")
    print(f"Label URL     : {data['label_url'] or 'Not available'}")

    if data["selected_rate"]:
        print(
            "Selected Rate : "
            f"{data['selected_rate']['carrier']} | "
            f"{data['selected_rate']['service']} | "
            f"{data['selected_rate']['rate']} {data['selected_rate']['currency']} | "
            f"Delivery Days: {data['selected_rate']['delivery_days']}"
        )
