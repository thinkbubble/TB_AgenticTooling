import os
from typing import Any, Dict, Optional, List
import json
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
DEFAULT_TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER") 

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    raise ValueError("TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN not found in .env file")


def initialize_twilio_api_client() -> Client:
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_text_message(
    destination_phone_number: str, 
    message_body_content: str, 
    sender_phone_number: Optional[str] = None) -> Any:
    twilio_api_client = initialize_twilio_api_client()
    resolved_sender_phone_number = sender_phone_number or DEFAULT_TWILIO_PHONE_NUMBER

    try:
        created_text_message = twilio_api_client.messages.create(
            to=destination_phone_number,
            from_=resolved_sender_phone_number,
            body=message_body_content
        )
        return created_text_message
    except TwilioRestException as twilio_api_error:
        print(f"Twilio API Error sending text message: {twilio_api_error}")
        return None


def initiate_voice_call(
    destination_phone_number: str, 
    twiml_instructions_url: str, 
    sender_phone_number: Optional[str] = None) -> Any:
    twilio_api_client = initialize_twilio_api_client()
    resolved_sender_phone_number = sender_phone_number or DEFAULT_TWILIO_PHONE_NUMBER

    try:
        created_voice_call = twilio_api_client.calls.create(
            to=destination_phone_number,
            from_=resolved_sender_phone_number,
            url=twiml_instructions_url
        )
        return created_voice_call
    except TwilioRestException as twilio_api_error:
        print(f"Twilio API Error making voice call: {twilio_api_error}")
        return None


def retrieve_message_details(unique_message_identifier: str) -> Any:
    twilio_api_client = initialize_twilio_api_client()
    
    try:
        retrieved_message_object = twilio_api_client.messages(unique_message_identifier).fetch()
        return retrieved_message_object
    except TwilioRestException as twilio_api_error:
        print(f"Twilio API Error fetching message details: {twilio_api_error}")
        return None


def retrieve_recent_messages_list(maximum_messages_to_retrieve: int = 20) -> List[Any]:
    twilio_api_client = initialize_twilio_api_client()
    
    try:
        recent_messages_list = twilio_api_client.messages.list(limit=maximum_messages_to_retrieve)
        return recent_messages_list
    except TwilioRestException as twilio_api_error:
        print(f"Twilio API Error listing recent messages: {twilio_api_error}")
        return []

def display_message_status_details(twilio_message_object) -> None:
    if not twilio_message_object:
        print("No message data provided.")
        return
        
    print("\nMessage Details:")
    print("-" * 60)
    print(f"Unique Identifier : {twilio_message_object.sid}")
    print(f"Destination       : {twilio_message_object.to}")
    print(f"Sender            : {twilio_message_object.from_}")
    print(f"Current Status    : {twilio_message_object.status}")
    print(f"Body Content      : {twilio_message_object.body}")
    print("\n RAW API RESPONSE PAYLOAD:")
    print("-" * 60)
    
    raw_data = getattr(twilio_message_object, '_properties', {})
    
    if raw_data:
        formatted_json = json.dumps(raw_data, indent=4, default=str)
        print(formatted_json)
    else:
        print("No raw data available for this object.")
    
    print("-" * 60)