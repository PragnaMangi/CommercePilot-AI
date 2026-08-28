import os
import requests
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

print("Loaded key:", api_key[:8] + "..." + api_key[-4:])

client = genai.Client(api_key=api_key)


# =========================================================
# TOOL 1: Search products
# =========================================================

def search_products(name: str = "", max_price: float = 100000):

    url = "http://127.0.0.1:8000/products/search/"

    response = requests.get(
        url,
        params={
            "name": name,
            "max_price": max_price
        }
    )

    return response.json()


# =========================================================
# TOOL 2: Check inventory
# =========================================================

def check_inventory(product_id: int):

    url = f"http://127.0.0.1:8000/products/inventory/{product_id}"

    response = requests.get(url)

    return response.json()


# =========================================================
# TOOL 3: Compare products
# =========================================================

def compare_products(product1: int, product2: int):

    url = "http://127.0.0.1:8000/products/compare/"

    response = requests.get(
        url,
        params={
            "product1": product1,
            "product2": product2
        }
    )

    return response.json()


# =========================================================
# TOOL 4: Add product to cart
# =========================================================

def add_to_cart(product_id: int, quantity: int = 1):

    url = "http://127.0.0.1:8000/cart/add"

    response = requests.post(
        url,
        params={
            "product_id": product_id,
            "quantity": quantity
        }
    )

    return response.json()


# =========================================================
# TOOL 5: View cart
# =========================================================

def view_cart():

    url = "http://127.0.0.1:8000/cart/"

    response = requests.get(url)

    return response.json()


# =========================================================
# TOOL 6: Remove product from cart
# =========================================================

def remove_from_cart(product_id: int):

    url = f"http://127.0.0.1:8000/cart/remove/{product_id}"

    response = requests.delete(url)

    return response.json()


# =========================================================
# TOOL 7: Update cart quantity
# =========================================================

def update_cart_quantity(product_id: int, quantity: int):

    url = f"http://127.0.0.1:8000/cart/update/{product_id}"

    response = requests.put(
        url,
        params={
            "quantity": quantity
        }
    )

    return response.json()


# =========================================================
# TOOL 8: Clear cart
# =========================================================

def clear_cart():

    url = "http://127.0.0.1:8000/cart/clear"

    response = requests.delete(url)

    return response.json()


# =========================================================
# DIRECT CART COMMANDS
# These commands DO NOT use Gemini
# =========================================================

def handle_direct_cart_command(message):

    message = message.lower().strip()

    # -----------------------------------------------------
    # SHOW CART
    # -----------------------------------------------------

    if message in [
        "show my cart",
        "show cart",
        "view my cart",
        "view cart",
        "my cart",
        "cart"
    ]:

        cart = view_cart()

        print("\nCommercePilot AI:")

        if not cart:
            print("Your cart is empty.")
            return True

        print("Here is your current cart:\n")

        total = 0

        for item in cart:

            product_id = item.get("product_id")
            quantity = item.get("quantity")
            item_total = item.get("total_price", 0)

            total += item_total

            print(
                f"Product ID: {product_id}"
            )

            print(
                f"Quantity: {quantity}"
            )

            print(
                f"Total Price: ₹{item_total:,.2f}"
            )

            print("-------------------------")

        print(f"Cart Total: ₹{total:,.2f}")
        print()

        return True


    # -----------------------------------------------------
    # CLEAR CART
    # -----------------------------------------------------

    if message in [
        "clear cart",
        "clear my cart",
        "empty cart",
        "empty my cart"
    ]:

        result = clear_cart()

        print("\nCommercePilot AI:")
        print(result)
        print()

        return True


    # -----------------------------------------------------
    # No direct command matched
    # -----------------------------------------------------

    return False


# =========================================================
# START AI AGENT
# =========================================================

def start_agent():

    # Create one chat session
    # This preserves the conversation

    chat = client.chats.create(
        model="gemini-3.6-flash",
        config={
            "tools": [
                search_products,
                check_inventory,
                compare_products,
                add_to_cart,
                view_cart,
                remove_from_cart,
                update_cart_quantity,
                clear_cart
            ]
        }
    )

    print("\n🤖 CommercePilot AI is ready!")
    print("Type 'exit' to stop.\n")

    while True:

        message = input("You: ")

        # -------------------------------------------------
        # EXIT
        # -------------------------------------------------

        if message.lower().strip() in [
            "exit",
            "quit",
            "bye"
        ]:

            print("\nCommercePilot AI: Goodbye! 👋")
            break


        try:

            # -------------------------------------------------
            # HANDLE SIMPLE CART COMMANDS WITHOUT GEMINI
            # -------------------------------------------------

            handled = handle_direct_cart_command(message)

            if handled:
                continue


            # -------------------------------------------------
            # USE GEMINI FOR AI REQUESTS
            # -------------------------------------------------

            response = chat.send_message(message)

            print("\nCommercePilot AI:")
            print(response.text)
            print()


        except Exception as error:

            print("\nError:")
            print(error)
            print()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    start_agent()