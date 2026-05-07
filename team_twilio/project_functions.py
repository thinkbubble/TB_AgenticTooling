
import os
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def build_response(success: bool, provider: str, msg_type: str,
                   sid=None, status=None, message=None, error=None, data=None):

    return {
        "success": success,
        "provider": provider,
        "type": msg_type,
        "sid": sid,
        "status": status,
        "message": message,
        "error": error,
        "data": data
    }


def send_text_message(destination_phone_number: str, message_body_content: str):

    try:
        msg = client.messages.create(
            to=destination_phone_number,
            from_=TWILIO_PHONE,
            body=message_body_content
        )

        return build_response(
            True, "twilio", "sms",
            sid=msg.sid,
            status=msg.status,
            message="SMS sent successfully"
        )

    except Exception as e:
        return build_response(False, "twilio", "sms", error=str(e))


def initiate_voice_call(destination_phone_number: str, message_text: str):

    try:
        vr = VoiceResponse()
        vr.say(message_text, voice="alice")

        call = client.calls.create(
            to=destination_phone_number,
            from_=TWILIO_PHONE,
            twiml=str(vr)
        )

        return build_response(
            True, "twilio", "voice",
            sid=call.sid,
            status=call.status,
            message="Call initiated"
        )

    except Exception as e:
        return build_response(False, "twilio", "voice", error=str(e))



def retrieve_message_details(sid: str):

    try:
        msg = client.messages(sid).fetch()

        return build_response(
            True, "twilio", "sms_detail",
            sid=msg.sid,
            status=msg.status,
            message=msg.body
        )

    except Exception as e:
        return build_response(False, "twilio", "sms_detail", error=str(e))


def retrieve_recent_messages_list(limit: int = 5):

    try:
        msgs = client.messages.list(limit=limit)

        data = [
            {
                "sid": m.sid,
                "to": m.to,
                "from": m.from_,
                "status": m.status,
                "body": m.body
            }
            for m in msgs
        ]

        return build_response(
            True, "twilio", "sms_history",
            data=data
        )

    except Exception as e:
        return build_response(False, "twilio", "sms_history", error=str(e))


def send_email(destination_email: str, subject: str, content: str):

    try:
        mail = Mail(
            from_email=EMAIL_FROM,
            to_emails=destination_email,
            subject=subject,
            plain_text_content=content
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        res = sg.send(mail)

        return build_response(
            True, "sendgrid", "email",
            status=str(res.status_code),
            message="Email sent successfully"
        )

    except Exception as e:

        return build_response(False, "sendgrid", "email", error=str(e))
    


