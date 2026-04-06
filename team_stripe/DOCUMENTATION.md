# Stripe Integration Module

## Functions

- get_client
    - Definition: Initializes Stripe using API key from `.env`.
    - Params:
        - No external params
    - Returns:
        - Stripe configured client

- create_customer
    - Definition: Creates a new Stripe customer.
    - Params:
        - name
        - email
    - Returns:
        - customer object
        - customer_id

- create_product
    - Definition: Creates a product in Stripe.
    - Params:
        - name
        - description
    - Returns:
        - product object
        - product_id

- create_price
    - Definition: Creates a price for a product.
    - Params:
        - product_id
        - unit_amount (in cents)
        - currency
    - Returns:
        - price object
        - price_id

- create_payment_intent
    - Definition: Creates a payment intent for payment processing.
    - Params:
        - amount (in cents)
        - currency
        - customer_id (optional)
    - Returns:
        - payment_intent object
        - client_secret

- confirm_payment
    - Definition: Confirms payment intent.
    - Params:
        - payment_intent_id
    - Returns:
        - payment status

- create_checkout_session
    - Definition: Creates Stripe Checkout session.
    - Params:
        - price_id
        - success_url
        - cancel_url
    - Returns:
        - session object
        - session_url

- retrieve_payment
    - Definition: Retrieves payment intent details.
    - Params:
        - payment_intent_id
    - Returns:
        - payment details

- list_customers
    - Definition: Lists all customers.
    - Params:
        - limit (optional)
    - Returns:
        - list of customers

- print_payment_details
    - Definition: Prints payment details.
    - Params:
        - payment_intent
    - Returns:
        - formatted output

## Workflow

- Payment Flow
    - create_customer
    - create_product
    - create_price
    - create_payment_intent
    - confirm_payment
    - retrieve_payment

- Checkout Flow
    - create_product
    - create_price
    - create_checkout_session

## Endpoints Used

- Customers API
- Products API
- Prices API
- Payment Intents API
- Checkout API