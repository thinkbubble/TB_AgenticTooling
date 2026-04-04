
# This is where you will write code that interacts with 
# your platform's functions in order to test it.



from functions import handle_stripe_event

def test_create_payment():
    mock_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer_email": "test@example.com"
            }
        }
    }

    handle_stripe_event(mock_event)

