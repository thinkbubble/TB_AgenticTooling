Functions

get_twilio_client

Definition: Creates and returns an authenticated Twilio REST client using credentials from .env.

Params:

No external params

Returns:

Twilio Client object

handle_twilio_webhook

Definition: Processes incoming HTTP POST requests from Twilio when an SMS is received.

Params:

From: The sender's phone number

Body: The text content of the message

Returns:

TwiML XML response (auto-reply)

Console log of sender and message

send_sms

Definition: Sends an outbound SMS or MMS message to a specified recipient.

Params:

to: Recipient number (E.164)

from: Your Twilio number

body: Message text

Returns:

Message SID

Delivery Status

create_phone_number

Definition: Searches for and purchases a new Twilio phone number based on location criteria.

Params:

country: (e.g., US, UK)

country_code: (e.g., +1, +44)

area_code: 3-digit local prefix

Returns:

Purchased Phone Number (E.164)

SID of the new resource

make_voice_call

Definition: Initiates an outbound voice call and executes TwiML instructions.

Params:

to: Recipient number

twiml: Instructions (e.g., <Say>) or a URL

Returns:

Call SID

Call Status (queued/initiated)

fetch_message_details

Definition: Retrieves metadata for a specific message using its unique SID.

Params:

message_sid: The unique ID of the SMS

Returns:

Date Sent

Error Code (if any)

Price/Currency

Workflow
Incoming SMS (Webhook)

Received POST request

Extract From and Body

Log to Terminal

Generate TwiML Response

Return XML to Twilio

Outbound Notification

Load .env Config

Validate Recipient Number

send_sms

Capture Message SID

Track Status via fetch_message_details

Provisioning Number

Select Country/Area Code

Search Available Numbers

create_phone_number

Update .env with new number

Endpoints Used
Messages API: Sending and retrieving SMS/MMS.

Calls API: Initiating and managing voice calls.

IncomingPhoneNumbers API: Provisioning new numbers.

AvailablePhoneNumbers API: Searching for numbers to buy.

TwiML: XML instructions for programmable logic.