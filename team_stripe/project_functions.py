
from dotenv import load_dotenv
# EVERYTHING in helper will be imported
from helper import *
#from new_helper import name_a_function
import os

load_dotenv()

YOUR_PLATFORM_KEY = os.getenv("YOUR_PLATFORM_KEY")

# YOUR CUSTOM WORK WILL GO HERE
# Naming convention should be robust
# Follow coding_guidelines.pdf on Sharepoint
# Follow documentation_guidelines.pdf on Sharepoint

import random

def create_phone_number():
    return f"+1{random.randint(2000000000, 9999999999)}"

def handle_stripe_event(event):
    # Identify event type
    event_type = event['type']

    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        print("Payment succeeded for:", session['customer_email'])
        # Add logic to store in database or trigger other actions

    elif event_type == 'invoice.payment_failed':
        invoice = event['data']['object']
        print("Payment failed for:", invoice['customer_email'])
    
    else:
        print("Unhandled event type:", event_type) 

