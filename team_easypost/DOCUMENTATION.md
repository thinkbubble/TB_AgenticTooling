# Functions

- get_client
    - Definition: Creates and returns authenticated EasyPost client using API key from `.env`.
    - Params:
        - No external params
    - Returns:
        - EasyPost client object

- is_international
    - Definition: Checks whether shipment is domestic or international by comparing sender and receiver country.
    - Params:
        - from_address
            - country
        - to_address
            - country
    - Returns:
        - True → international
        - False → domestic

- create_shipment
    - Definition: This function creates shipment object using EasyPost API.
    - Params:
        - from_address
            - name
            - street1
            - city
            - state
            - zip
            - country
            - phone
            - email
        - to_address
            - name
            - street1
            - city
            - state
            - zip
            - country
        - parcel
            - length
            - width
            - height
            - weight
        - customs_info
            - optional for international shipment
    - Returns:
        - shipment object
        - shipment_id
        - available rates

- create_customs_info
    - Definition: Creates customs item and customs info for international shipments.
    - Params:
        - item_description
        - item_value
        - item_weight
    - Returns:
        - customs_info_id

- get_lowest_rate
    - Definition: Selects and returns the lowest shipping rate.
    - Params:
        - shipment
    - Returns:
        - lowest rate object
        - carrier
        - service
        - rate

- buy_label
    - Definition: Purchases shipping label using selected shipment rate.
    - Params:
        - shipment_id
        - rate
    - Returns:
        - purchased shipment object
        - tracking_code
        - label_url
        - selected_rate

- track_shipment
    - Definition: Tracks shipment using EasyPost tracking API.
    - Params:
        - tracking_code
        - carrier (optional)
    - Returns:
        - tracker_id
        - tracking_code
        - tracking_status

- print_rates
    - Definition: Prints all available shipping rates in clean readable format.
    - Params:
        - shipment
    - Returns:
        - printed shipping rates

- print_shipment_details
    - Definition: Prints purchased shipment details.
    - Params:
        - shipment
    - Returns:
        - shipment_id
        - tracking_code
        - label_url
        - selected_rate
        - status

# Workflow

- Domestic Shipping
    - from_address
    - to_address
    - parcel
    - create_shipment
    - get_lowest_rate
    - buy_label
    - track_shipment

- International Shipping
    - from_address
    - to_address
    - parcel
    - create_customs_info
    - create_shipment
    - get_lowest_rate
    - buy_label
    - track_shipment

# Endpoints Used

- Address API
- Shipment API
- Parcel API
- Buy Label API
- Tracker API
- Customs Item API
- Customs Info API