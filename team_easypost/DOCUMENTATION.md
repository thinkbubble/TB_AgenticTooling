- get_client

  - Definition: Creates and returns an authenticated EasyPost client using the API key from .env

    - Params:

      - No external params
  - Returns:

    - EasyPost client object

- is_international

  - Definition: Checks whether the shipment is domestic or international by comparing sender and receiver country

    - Params:

      - from_address

        - country
      - to_address

        - country
    - Returns:

      - True → international shipment
      - False → domestic shipment

- validate_required_fields

  - Definition: Validates that required fields exist in a given dictionary

    - Params:

      - data → input dictionary
      - required_fields → list of required keys
      - object_name → name used for error messages
    - Returns:

      - None (raises error if validation fails)

- validate_parcel

  - Definition: Validates parcel dimensions and weight before shipment creation

    - Params:

      - parcel

        - length
        - width
        - height
        - weight
    - Returns:

      - None (raises error if invalid)

- validate_address_input

  - Definition: Validates minimum required fields for an address before verification

    - Params:

      - address

        - street1
        - city
        - state
        - zip
        - country
    - Returns:

      - None (raises error if invalid)

- validate_address

  - Definition: Verifies an address using EasyPost before shipment creation

    - Params:

      - address

        - name
        - street1
        - city
        - state
        - zip
        - country
        - phone
        - email
      - strict

        - True → raises error if verification fails
        - False → returns verification result
      - verify_carrier (optional)
    - Returns:

      - Verified address as dictionary

- create_customs_info

  - Definition: Creates customs information required for international shipments

    - Params:

      - items

        - description
        - quantity
        - value
        - weight
        - origin_country
        - hs_tariff_number (optional)
      - customs_signer
      - contents_type
      - non_delivery_option
      - restriction_type
      - eel_pfc (optional)
    - Returns:

      - Dictionary containing customs_info_id

- create_shipment

  - Definition: Creates a shipment using EasyPost with optional customs logic

    - Params:

      - from_address
      - to_address
      - parcel
      - customs_info (optional)
      - verify_addresses
    - Returns:

      - EasyPost shipment object

- get_available_rates

  - Definition: Extracts and formats available shipping rates from a shipment

    - Params:

      - shipment
    - Returns:

      - List of normalized rate dictionaries

- select_best_rate

  - Definition: Selects the best shipping rate based on business rules

    - Params:

      - shipment
      - preferred_carriers (optional)
      - preferred_service (optional)
      - max_delivery_days (optional)
      - cheapest
    - Returns:

      - Selected rate as dictionary

- buy_label

  - Definition: Purchases a shipping label using selected rate

    - Params:

      - shipment_id
      - rate
      - insurance_amount (optional)
    - Returns:

      - Updated EasyPost shipment object

- insure_existing_shipment

  - Definition: Adds insurance to an already created shipment

    - Params:

      - shipment_id
      - insurance_amount
    - Returns:

      - Updated shipment object

- track_shipment

  - Definition: Registers tracking for a shipment using tracking code

    - Params:

      - tracking_code
      - carrier (optional)
    - Returns:

      - Tracker details as dictionary

- safe_float

  - Definition: Safely converts a value to float

    - Params:

      - value
    - Returns:

      - Float value or None

- _get_value

  - Definition: Safely extracts values from object or dictionary

    - Params:

      - obj
      - key
    - Returns:

      - Value or None

- address_to_dict

  - Definition: Converts EasyPost address object into dictionary format

    - Params:

      - address_obj
    - Returns:

      - Address dictionary

- rate_to_dict

  - Definition: Converts rate object into dictionary format

    - Params:

      - rate
    - Returns:

      - Rate dictionary

- shipment_to_dict

  - Definition: Converts shipment object into structured dictionary

    - Params:

      - shipment
    - Returns:

      - Shipment dictionary

- tracker_to_dict

  - Definition: Converts tracker object into structured dictionary

    - Params:

      - tracker
    - Returns:

      - Tracker dictionary

- print_shipment_details

  - Definition: Prints shipment details in a readable format

    - Params:

      - shipment
    - Returns:

      - None (console output)

- process_shipment

  - Definition: End-to-end workflow that handles full shipment process

    - Params:

      - from_address
      - to_address
      - parcel
      - customs_items (optional)
      - customs_signer (optional)
      - insurance_amount (optional)
      - verify_addresses
      - preferred_carriers
      - max_delivery_days
      - preferred_service
    - Returns:

      - Final purchased shipment object