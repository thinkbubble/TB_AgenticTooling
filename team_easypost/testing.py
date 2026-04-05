from project_functions import (
    is_international,
    create_shipment,
    create_customs_info,
    get_lowest_rate,
    buy_label,
    track_shipment,
    print_rates,
    print_shipment_details
)

from_address = {
    "name": "Sender Name",
    "street1": "417 Montgomery Street",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94104",
    "country": "US",
    "phone": "4155551212",
    "email": "sender@example.com"
}

to_address = {
    "name": "Receiver Name",
    "street1": "388 Townsend Street",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94107",
    "country": "US" # if we change country to CA it will be considered as international shipping.
}

parcel = {
    "length": 10,
    "width": 8,
    "height": 4,
    "weight": 32
}


def main():
    try:
        print("Checking shipment type...")

        if is_international(from_address, to_address):
            print("International shipment detected.")

            customs_info = create_customs_info(
                item_description="T-shirt",
                item_value=25.0,
                item_weight=16.0
            )

            shipment = create_shipment(
                from_address=from_address,
                to_address=to_address,
                parcel=parcel,
                customs_info=customs_info
            )
        else:
            print("Domestic shipment detected.")

            shipment = create_shipment(
                from_address=from_address,
                to_address=to_address,
                parcel=parcel
            )

        print(f"\nShipment created successfully: {shipment.id}")

        print_rates(shipment)

        lowest_rate = get_lowest_rate(shipment)

        print("\nLowest Rate Chosen:")
        print("-" * 60)
        print(
            f"Carrier: {lowest_rate.carrier}, "
            f"Service: {lowest_rate.service}, "
            f"Rate: {lowest_rate.rate} {lowest_rate.currency}"
        )

        bought_shipment = buy_label(shipment.id, lowest_rate)

        print("\nLabel purchased successfully.")
        print_shipment_details(bought_shipment)

        tracking_code = getattr(bought_shipment, "tracking_code", None)

        if tracking_code:
            print("\nTracking code generated from shipment:")
            print("-" * 60)
            print(f"Tracking Code: {tracking_code}")

            try:
                print("\nTrying tracker.create()...")
                tracker = track_shipment(tracking_code)
                print("-" * 60)
                print(f"Tracker ID    : {tracker.id}")
                print(f"Tracking Code : {tracker.tracking_code}")
                print(f"Status        : {tracker.status}")
            except Exception as tracking_error:
                print("\nTracker creation skipped in test mode.")
                print(f"Reason: {tracking_error}")
        else:
            print("\nNo tracking code available yet.")

    except Exception as e:
        print("\nError occurred:")
        print(str(e))


if __name__ == "__main__":
    main()