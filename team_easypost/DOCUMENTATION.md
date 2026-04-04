# Functions

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
      - False → returns verification result without strict failure
    - verify_carrier
      - optional carrier-specific verification
  - Returns:
    - Verified EasyPost address object

- create_customs_info
  - Definition: Creates customs information for international shipments using one or more customs items
  - Params:
    - items
      - description
      - quantity
      - value
      - weight
      - hs_tariff_number
      - origin_country
    - customs_signer
    - contents_type
    - non_delivery_option
    - restriction_type
    - eel_pfc
  - Returns:
    - Dictionary containing customs info ID

- create_shipment
  - Definition: Creates a shipment in EasyPost using sender address, receiver address, parcel details, and optional customs info
  - Params:
    - from_address
    - to_address
    - parcel
      - length
      - width
      - height
      - weight
    - customs_info
  - Returns:
    - EasyPost shipment object

- print_rates
  - Definition: Displays all available shipping rates returned for the shipment
  - Params:
    - shipment
  - Returns:
    - Prints all available rates

- select_best_rate
  - Definition: Selects the best shipping rate based on business rules instead of only the cheapest option
  - Params:
    - shipment
    - preferred_carriers
    - preferred_services
    - max_rate
    - max_delivery_days
  - Returns:
    - Best matching rate object

- get_lowest_rate
  - Definition: Returns the cheapest available shipping rate from the shipment
  - Params:
    - shipment
  - Returns:
    - Lowest rate object

- buy_label
  - Definition: Purchases a shipping label for the selected shipment and rate with optional insurance
  - Params:
    - shipment_id
    - rate
    - insurance_amount
  - Returns:
    - Purchased shipment object

- insure_existing_shipment
  - Definition: Adds insurance to an already created or purchased shipment
  - Params:
    - shipment_id
    - insurance_amount
  - Returns:
    - Insured shipment object

- track_shipment
  - Definition: Creates a tracker in EasyPost using a tracking code
  - Params:
    - tracking_code
    - carrier
  - Returns:
    - EasyPost tracker object

- address_to_dict
  - Definition: Converts an EasyPost address object into a clean dictionary
  - Params:
    - address_obj
  - Returns:
    - Dictionary with address details

- rate_to_dict
  - Definition: Converts a shipping rate object into a structured dictionary
  - Params:
    - rate
  - Returns:
    - Dictionary with rate details

- shipment_to_dict
  - Definition: Converts a shipment object into a structured dictionary
  - Params:
    - shipment
  - Returns:
    - Dictionary with shipment details

- tracker_to_dict
  - Definition: Converts a tracker object into a structured dictionary
  - Params:
    - tracker
  - Returns:
    - Dictionary with tracker details

- print_shipment_details
  - Definition: Prints shipment details in a readable format after label purchase
  - Params:
    - shipment
  - Returns:
    - Prints shipment summary


# Testing Workflow

- from_address
  - Sender address used for shipment creation

- to_address
  - Receiver address used for shipment creation
  - If country changes from US to CA, shipment becomes international

- parcel
  - Stores package dimensions and weight

- customs_items
  - Stores item details for customs generation

- preferred_carriers
  - Preferred carriers for business rule selection

- preferred_services
  - Preferred service filters

- max_rate
  - Maximum allowed shipping cost

- max_delivery_days
  - Maximum allowed delivery speed

- insurance_amount
  - Optional shipment insurance

- test_tracking_code
  - EasyPost sandbox tracking number for test mode

- pretty_print
  - Utility function for formatted JSON display

- main
  - Main execution flow
  - Steps:
    - Verify addresses
    - Detect domestic vs international shipment
    - Create customs info if needed
    - Create shipment
    - Show rates
    - Select best rate
    - Buy label
    - Print shipment details
    - Try shipment tracking
    - Use sandbox fallback tracker if needed


# Overall Workflow

1. Load API key from .env
2. Create EasyPost client
3. Verify addresses
4. Check domestic vs international
5. Create customs for international shipment
6. Create shipment
7. Fetch shipping rates
8. Select best rate
9. Buy label
10. Print shipment JSON
11. Create tracker
12. Use sandbox fallback tracker if EasyPost test mode rejects real tracking


# Benefits of Updated Version

- Address verification before shipment creation
- Dynamic customs support
- Business-rule-based smart rate selection
- Optional insurance support
- JSON-friendly structured output
- Better exception handling
- Sandbox-safe tracking fallback


# Project Summary

This project is an end-to-end EasyPost shipping workflow built in Python.

Features:
- address verification
- domestic and international shipment detection
- customs generation
- shipment creation
- smart rate selection
- label purchase
- insurance
- tracking
- structured JSON output