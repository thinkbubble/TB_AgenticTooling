import json

from project_functions import (
    is_international,
    validate_address,
    create_shipment,
    create_customs_info,
    select_best_rate,
    buy_label,
    track_shipment,
    print_shipment_details,
)

from_address = {
    "name": "Sender Name",
    "street1": "417 Montgomery Street",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94104",
    "country": "US",
    "phone": "4155551212",
    "email": "sender@example.com",
}

to_address = {
    "name": "Receiver Name",
    "street1": "388 Townsend Street",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94107",
    "country": "US",   # Change to "CA" to test international
    "phone": "4155553434",
    "email": "receiver@example.com",
}

parcel = {
    "length": 10,
    "width": 8,
    "height": 4,
    "weight": 32,
}

customs_items = [
    {
        "description": "T-shirt",
        "quantity": 2,
        "value": 25.0,
        "weight": 16.0,
        "hs_tariff_number": "610910",
        "origin_country": "US",
    },
    {
        "description": "Cap",
        "quantity": 1,
        "value": 15.0,
        "weight": 8.0,
        "hs_tariff_number": "650500",
        "origin_country": "US",
    },
]

preferred_carriers = ["USPS", "UPS"]
preferred_service = None
max_delivery_days = 5
insurance_amount = "100.00"

# EasyPost sandbox-approved test tracking number
test_tracking_code = "EZ1000000001"


def pretty_print(title: str, data) -> None:
    print(f"\n{title}")
    print("-" * 80)
    print(json.dumps(data, indent=2, default=str))


def main():
    try:
        print("Step 1: Verifying addresses...")

        verified_from = validate_address(from_address, strict=True)
        verified_to = validate_address(to_address, strict=True)

        pretty_print("Verified From Address", verified_from)
        pretty_print("Verified To Address", verified_to)

        print("\nStep 2: Determining shipment type...")

        customs_info = None
        if is_international(from_address, to_address):
            print("International shipment detected.")

            customs_info = create_customs_info(
                items=customs_items,
                customs_signer="Sender Name",
                contents_type="merchandise",
                non_delivery_option="return",
                restriction_type="none",
            )

            pretty_print("Customs Info", customs_info)
        else:
            print("Domestic shipment detected.")

        shipment = create_shipment(
            from_address=from_address,
            to_address=to_address,
            parcel=parcel,
            customs_info=customs_info,
            verify_addresses=False,
        )

        print(f"\nStep 3: Shipment created successfully: {shipment['shipment_id']}")
        print_shipment_details(shipment)
        pretty_print("Shipment JSON", shipment)

        print("\nStep 4: Selecting best rate...")

        selected_rate = select_best_rate(
            shipment=shipment,
            preferred_carriers=preferred_carriers,
            max_delivery_days=max_delivery_days,
            preferred_service=preferred_service,
            cheapest=True,
        )

        pretty_print("Selected Rate", selected_rate)

        print("\nStep 5: Buying label...")

        bought_shipment = buy_label(
            shipment_id=shipment["shipment_id"],
            rate=selected_rate,
            insurance_amount=insurance_amount,
        )

        print("\nLabel purchased successfully.")
        print_shipment_details(bought_shipment)
        pretty_print("Bought Shipment JSON", bought_shipment)

        tracking_code = bought_shipment.get("tracking_code")

        print("\nStep 6: Tracking setup...")

        if tracking_code:
            print(f"Shipment tracking code generated: {tracking_code}")

            try:
                tracker = track_shipment(tracking_code=tracking_code)
                pretty_print("Tracker JSON", tracker)

            except RuntimeError as exc:
                print("\nTracker creation skipped for shipment tracking code in EasyPost test mode.")
                print(str(exc))
                print(f"\nTrying EasyPost sandbox test tracking code instead: {test_tracking_code}")

                sandbox_tracker = track_shipment(tracking_code=test_tracking_code)
                pretty_print("Sandbox Tracker JSON", sandbox_tracker)

        else:
            print("No shipment tracking code available yet.")
            print(f"\nTrying EasyPost sandbox test tracking code instead: {test_tracking_code}")

            sandbox_tracker = track_shipment(tracking_code=test_tracking_code)
            pretty_print("Sandbox Tracker JSON", sandbox_tracker)

    except ValueError as exc:
        print("\nValidation Error:")
        print(str(exc))

    except RuntimeError as exc:
        print("\nRuntime Error:")
        print(str(exc))

    except Exception as exc:
        print("\nUnexpected Error:")
        print(str(exc))


if __name__ == "__main__":
    main()