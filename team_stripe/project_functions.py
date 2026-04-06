
from dotenv import load_dotenv
# EVERYTHING in helper will be imported
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from helper import *
#from new_helper import name_a_function
import os

load_dotenv()

YOUR_PLATFORM_KEY = os.getenv("YOUR_PLATFORM_KEY")

# YOUR CUSTOM WORK WILL GO HERE
# Naming convention should be robust
# Follow coding_guidelines.pdf on Sharepoint
# Follow documentation_guidelines.pdf on Sharepoint


import os
import stripe
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

STRIPE_API_KEY = os.getenv("STRIPE_SECRET_KEY")
if not STRIPE_API_KEY:
    raise ValueError("STRIPE_SECRET_KEY not found in .env")

stripe.api_key = STRIPE_API_KEY


def get_client():
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    return stripe


def create_customer(name: str, email: str):
    customer = stripe.Customer.create(
        name=name,
        email=email
    )
    return customer


def create_product(name: str, description: str):
    product = stripe.Product.create(
        name=name,
        description=description
    )
    return product


def create_price(product_id: str, unit_amount: int, currency: str = "usd"):
    price = stripe.Price.create(
        product=product_id,
        unit_amount=unit_amount,
        currency=currency
    )
    return price


def create_payment_intent(amount: int, currency: str = "usd", customer_id: Optional[str] = None):
    payment_intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        customer=customer_id
    )
    return payment_intent


def confirm_payment(payment_intent_id: str):
    return stripe.PaymentIntent.confirm(payment_intent_id)


def create_checkout_session(price_id: str, success_url: str, cancel_url: str):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": price_id,
            "quantity": 1
        }],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url
    )
    return session


def retrieve_payment(payment_intent_id: str):
    return stripe.PaymentIntent.retrieve(payment_intent_id)


def list_customers(limit: int = 5):
    return stripe.Customer.list(limit=limit)


def print_payment_details(payment_intent):
    print("\nPayment Details:")
    print("-" * 60)
    print(f"Payment ID   : {payment_intent.id}")
    print(f"Amount       : {payment_intent.amount}")
    print(f"Currency     : {payment_intent.currency}")
    print(f"Status       : {payment_intent.status}")