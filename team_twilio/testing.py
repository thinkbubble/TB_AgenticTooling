import time


from project_functions import (
    initiate_voice_call,
    send_text_message,
    retrieve_message_details,
    retrieve_recent_messages_list,
    display_message_status_details
)


twilio_test_config = {
    "target_phone_number": "+15613245868",  
    "test_message_content": "Twilio workflow executed successfully",
    "network_delay_seconds": 2
}

def test_voice():
    print(" Attempting to call your phone")
    
    demo_twiml_url = "http://demo.twilio.com/docs/voice.xml"
    
    my_cell_number = "+15613245868" 

    call = initiate_voice_call(
        destination_phone_number=my_cell_number,
        twiml_instructions_url=demo_twiml_url
    )

    if call:
        print(f"Call initiated (Call SID: {call.sid})")
    else:
        print("Failed to initiate call")

if __name__ == "__main__":
    test_voice()

def main():
    try:
        print("Starting Twilio Communication Workflow\n")

        print("Attempting to dispatch text message")
        dispatched_message = send_text_message(
            destination_phone_number=twilio_test_config["target_phone_number"],
            message_body_content=twilio_test_config["test_message_content"]
        )

        
        if dispatched_message:
            print(f"\nText message dispatched successfully! Identifier: {dispatched_message.sid}")
            display_message_status_details(dispatched_message)

             
            print(f"\nWaiting {twilio_test_config['network_delay_seconds']} seconds for network processing...")
            time.sleep(twilio_test_config["network_delay_seconds"])

            
            print("\nFetching updated message details from the server...")
            updated_message_details = retrieve_message_details(
                unique_message_identifier=dispatched_message.sid
            )
            
            if updated_message_details:
                display_message_status_details(updated_message_details)
            else:
                print("Could not retrieve updated message details.")

        else:
            print("\nWorkflow Halted: Failed to dispatch text message.")
            print("Please ensure your .env variables and verified phone numbers are correct.")

        
        print("\nRetrieving recent message history...")
        recent_messages_list = retrieve_recent_messages_list(maximum_messages_to_retrieve=3)
        
        if recent_messages_list:
            print("-" * 60)
            for list_index, historical_message in enumerate(recent_messages_list, start=1):
                print(
                    f"[{list_index}] Destination: {historical_message.to} | "
                    f"Status: {historical_message.status} | "
                    f"Content snippet: '{historical_message.body[:15]}...'"
                )
        else:
            print("No recent messages found in history.")

    
    except Exception as workflow_execution_error:
        print("\nAn unexpected error occurred during the Twilio workflow:")
        print(str(workflow_execution_error))


if __name__ == "__main__":
    main()