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

EASYPOST_API_KEY = os.getenv("EASYPOST_API_KEY")
if not EASYPOST_API_KEY:
    raise ValueError("EASYPOST_API_KEY not found in .env file")

client = easypost.EasyPostClient(EASYPOST_API_KEY)

# SAMPLE DATA
def get_client():
    
    api_key = os.getenv("EASYPOST_API_KEY")
    if not api_key:
        raise ValueError("EASYPOST_API_KEY not found in .env")
    return easypost.EasyPostClient(api_key)

def is_international(from_address: Dict[str, Any], to_address: Dict[str, Any]) -> bool:
    
    from_country = from_address.get("country", "").strip().upper()
    to_country = to_address.get("country", "").strip().upper()
    return from_country != to_country


def create_shipment(
    from_address: Dict[str, Any],
    to_address: Dict[str, Any],
    parcel: Dict[str, Any],
    customs_info: Optional[Dict[str, Any]] = None
):
   
    client = get_client()

    shipment_data = {
        "from_address": from_address,
        "to_address": to_address,
        "parcel": parcel
    }

    if customs_info:
        shipment_data["customs_info"] = customs_info

    shipment = client.shipment.create(**shipment_data)
    return shipment


def create_customs_info(item_description: str, item_value: float, item_weight: float):
    
    client = get_client()

    customs_item = client.customs_item.create(
        description=item_description,
        quantity=1,
        value=item_value,
        weight=item_weight,
        hs_tariff_number="420292",
        origin_country="US"
    )

    customs_info = client.customs_info.create(
        customs_certify=True,
        customs_signer="Sender Name",
        contents_type="merchandise",
        customs_items=[{"id": customs_item.id}]
    )

    return {"id": customs_info.id}


def get_lowest_rate(shipment):
    
    return shipment.lowest_rate()


def buy_label(shipment_id: str, rate):
    
    client = get_client()
    bought_shipment = client.shipment.buy(shipment_id, rate=rate)
    return bought_shipment


def track_shipment(tracking_code: str, carrier: Optional[str] = None):
    
    client = get_client()

    if carrier:
        tracker = client.tracker.create(
            tracking_code=tracking_code,
            carrier=carrier
        )
    else:
        tracker = client.tracker.create(
            tracking_code=tracking_code
        )

    return tracker


def print_rates(shipment):
   
    print("\nAvailable Rates:")
    print("-" * 60)
    for index, rate in enumerate(shipment.rates, start=1):
        print(
            f"{index}. Carrier: {rate.carrier}, "
            f"Service: {rate.service}, "
            f"Rate: {rate.rate} {rate.currency}"
        )


def print_shipment_details(shipment):
    
    print("\nShipment Details:")
    print("-" * 60)
    print(f"Shipment ID   : {shipment.id}")
    print(f"Status        : {shipment.status}")
    print(f"Tracking Code : {getattr(shipment, 'tracking_code', 'Not available')}")

    if getattr(shipment, "postage_label", None):
        print(f"Label URL     : {shipment.postage_label.label_url}")

    if getattr(shipment, "selected_rate", None):
        print(
            f"Selected Rate : {shipment.selected_rate.carrier} | "
            f"{shipment.selected_rate.service} | "
            f"{shipment.selected_rate.rate} {shipment.selected_rate.currency}"
        )
