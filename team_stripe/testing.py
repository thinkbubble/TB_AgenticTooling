
# This is where you will write code that interacts with 
# your platform's functions in order to test it.
from project_functions import (
    create_customer,
    create_product,
    create_price,
    create_payment_intent,
    confirm_payment,
    retrieve_payment,
    print_payment_details
)
 # 
def main():
    try:
        print("Creating customer...")
        customer = create_customer("Sai Siva", "test@example.com")

        print("Creating product...")
        product = create_product("T-Shirt", "Comfortable cotton t-shirt")

        print("Creating price...")
        price = create_price(product.id, 2000)  # $20

        print("Creating payment intent...")
        payment_intent = create_payment_intent(
            amount=2000,
            customer_id=customer.id
        )

        print("Confirming payment...")
        confirmed = confirm_payment(payment_intent.id)

        print("Retrieving payment...")
        payment = retrieve_payment(payment_intent.id)

        print_payment_details(payment)

    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    main()

