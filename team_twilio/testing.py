import time
import json

from project_functions import (
    initiate_voice_call,
    send_text_message,
    retrieve_message_details,
    retrieve_recent_messages_list,
    send_email
)

twilio_test_config = {
    "target_phone_number": "+15613245868",  
    "test_message_content": "Twilio workflow executed successfully",
    "network_delay_seconds": 2
}

def test_voice():
    try:
        my_cell_number = twilio_test_config["target_phone_number"]

        call = initiate_voice_call(
            destination_phone_number=my_cell_number,
            message_text="Hello Meghana, your Twilio integration is working!"
        )

        if call and call.get("success"):
            print(f"Voice call successful. SID: {call.get('sid')}")
        else:
            print("Voice call failed. Check Twilio credentials or phone number.")

        return call

    except Exception as e:
        print(f"Voice test error: {e}")
        return None


def test_text_message_workflow():
    results = {}

    try:
        dispatched_message = send_text_message(
            destination_phone_number=twilio_test_config["target_phone_number"],
            message_body_content=twilio_test_config["test_message_content"]
        )

        results["dispatched_message"] = dispatched_message

        print("\nSMS Response:")
        print(json.dumps(dispatched_message, indent=2))

        # ✔ SAFE CHECK
        if not dispatched_message or not isinstance(dispatched_message, dict):
            results["error"] = "No valid response from Twilio"
            return results

        sid = dispatched_message.get("sid")

        if dispatched_message.get("success") and sid:

            print(f"SMS INITIATED. SID: {sid}")
            print("STATUS:", dispatched_message.get("status"))

            time.sleep(twilio_test_config["network_delay_seconds"])

            results["updated_message_details"] = retrieve_message_details(sid)
            results["recent_messages"] = retrieve_recent_messages_list(limit=3)

        else:
            results["error"] = dispatched_message.get("error", "SMS failed at Twilio level")
            results["updated_message_details"] = None
            results["recent_messages"] = None

    except Exception as e:
        results["error"] = str(e)

    return results

def test_email():
    print("\n--- Email Test ---\n")

    result = send_email(
        destination_email="meghana.bellamkonda.20@gmail.com",
        subject="Integration Test",
        content="Hello Meghana, email integration is working!"
    )

    if result:
        print("Email Result:")
        print(json.dumps(result, indent=2))
    else:
        print("Email failed or returned None")

    return result

if __name__ == "__main__":

    print("\n--- Voice Test ---\n")
    test_voice()

    print("\n--- SMS Workflow Test ---\n")
    workflow_results = test_text_message_workflow()
    print(json.dumps(workflow_results, indent=2))

    print("\nEmail Result:")
    email_result = test_email()

    print("\n===== TEST SUMMARY =====")
    print(json.dumps({
        "voice": "completed",
        "sms": workflow_results,
        "email": email_result
    }, indent=2))