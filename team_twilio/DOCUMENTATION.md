# Twilio Communication Integration System

---

## Project Summary
- Flask-based communication system for SMS, voice, and email
- Uses Twilio API for SMS and voice call handling
- Uses SendGrid API for email delivery
- Supports incoming webhooks (SMS, calls, email)
- Includes automated testing script for API verification
- Built for end-to-end communication workflow testing

---

## Technologies Used
- Python
- Flask
- Twilio API
- SendGrid API
- dotenv

---

## Project Structure
- app.py → Flask webhook server (SMS, calls, email)
- functions.py → API integration layer (Twilio + SendGrid)
- testing.py → Automated test execution script
- .env → Environment variables for API keys

---

## Run Instructions

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Start Flask Server
```bash
python app.py
```

### Run Tests
```bash
python testing.py
```

---

## Output Locations
- SMS results → terminal logs
- Voice call results → terminal logs
- Email results → terminal logs
- Webhook activity → Flask console output
- Test summary → JSON printed in terminal

---

## Success Indicators
- SMS sent successfully (SID generated)
- Voice call received successfully
- Email delivered successfully
- Flask webhook logs appear in terminal
- Testing script prints JSON summary without errors

---

## Common Failures
- Invalid Twilio SID/Auth Token
- Unverified phone number (Twilio trial restriction)
- Missing SendGrid API key
- Flask server not running
- Incorrect or missing .env variables

---

## End-to-End Flow
- Run testing.py
- SMS request sent via Twilio API
- Voice call triggered via Twilio Voice API
- Email sent via SendGrid API
- Incoming webhooks handled by Flask
- TwiML responses returned for SMS/calls
- Logs printed in terminal
- Final test results displayed as JSON

---

## Webhook Endpoints
- /webhook/message → Handles incoming SMS
- /webhook/answercall → Handles incoming voice calls
- /receive-email → Handles incoming email data

---

## Configuration (.env)

| Name | Purpose | Example | Required |
|------|--------|---------|----------|
| TWILIO_ACCOUNT_SID | Twilio account ID | ACxxxxx | Y |
| TWILIO_AUTH_TOKEN | Twilio authentication token | xxxxx | Y |
| TWILIO_PHONE_NUMBER | Twilio registered number | +1561xxxx | Y |
| SENDGRID_API_KEY | SendGrid API key | SG.xxxx | Y |
| EMAIL_FROM | Verified sender email | test@gmail.com | Y |

---

## Functions Index

---

## app.py

### sms_webhook()
- Handles incoming SMS messages
- Inputs: HTTP request data
- Outputs: TwiML XML response
- Errors: missing request parameters

---

### answercall_webhook()
- Handles incoming voice calls
- Inputs: HTTP request data
- Outputs: VoiceResponse XML
- Errors: missing caller number

---

### receive_email()
- Handles incoming email webhook data
- Inputs: form data (from, subject, text)
- Outputs: HTTP 200 OK response
- Errors: missing email fields

---

## functions.py

### send_text_message(destination_phone_number, message_body_content)
- Sends SMS via Twilio API
- Inputs: phone number, message text
- Outputs: dictionary response (SID, status, success)
- Errors: invalid number, API failure

---

### initiate_voice_call(destination_phone_number, message_text)
- Initiates voice call using Twilio
- Inputs: phone number, spoken message
- Outputs: dictionary response (call SID, status)
- Errors: invalid number, API failure

---

### retrieve_message_details(sid)
- Retrieves details of a specific SMS
- Inputs: message SID
- Outputs: message status dictionary
- Errors: invalid SID, message not found

---

### retrieve_recent_messages_list(limit)
- Fetches recent SMS messages
- Inputs: limit (number of messages)
- Outputs: list of message dictionaries
- Errors: API failure

---

### send_email(destination_email, subject, content)
- Sends email using SendGrid API
- Inputs: email, subject, message body
- Outputs: API response dictionary
- Errors: invalid API key, sender not verified

---

### build_response(success, provider, msg_type, sid, status, message, error, data)
- Standard response formatter
- Inputs: success flag, provider, type, metadata
- Outputs: structured dictionary response
- Errors: none

---

## testing.py

### test_voice()
- Tests voice call functionality
- Inputs: predefined phone number
- Outputs: call response dictionary
- Errors: Twilio API failure

---

### test_text_message_workflow()
- Tests full SMS workflow (send + retrieve)
- Inputs: test configuration values
- Outputs: SMS response + message history
- Errors: SID failure, API failure

---

### test_email()
- Tests SendGrid email sending
- Inputs: predefined email content
- Outputs: email response dictionary
- Errors: authentication failure

---

## Notes / Assumptions
- Twilio account is active and configured
- SendGrid sender email is verified
- Internet connection required for APIs
- Flask runs in debug mode
- Phone numbers use E.164 format

---

## Data Assumptions
- Message SIDs are unique identifiers
- Email addresses are valid format
- API responses are JSON-based
- Webhooks send standard Twilio payloads

---

## Rate Limits
- Twilio trial accounts restrict messaging
- SendGrid free tier limits daily emails
- Flask debug server not production ready

---

## Known Limitations
- No database storage
- No frontend UI
- Console-based logging only
- Trial account restrictions apply

---

## Future Improvements
- Add database storage (MongoDB/MySQL)
- Build frontend dashboard (React/Flask UI)
- Add retry mechanism for failed API requests