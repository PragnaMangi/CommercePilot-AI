from fastapi import APIRouter
from typing import Dict, Any, Optional
import requests
import re
import os
import json

from dotenv import load_dotenv
from google import genai


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
)

API = "http://127.0.0.1:8000"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# =========================================================
# GEMINI CLIENT
# =========================================================

gemini_client = None

if GOOGLE_API_KEY:
    try:
        gemini_client = genai.Client(
            api_key=GOOGLE_API_KEY
        )
    except Exception:
        gemini_client = None


# =========================================================
# AGENT MEMORY
# =========================================================

assistant_state: Dict[str, Any] = {
    "last_products": [],
    "selected_product": None,
    "last_intent": None
}


# =========================================================
# HTTP HELPERS
# =========================================================

def api_get(path, params=None):

    response = requests.get(
        f"{API}{path}",
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def api_post(path, params=None):

    response = requests.post(
        f"{API}{path}",
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def api_put(path, params=None):

    response = requests.put(
        f"{API}{path}",
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def api_delete(path):

    response = requests.delete(
        f"{API}{path}",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# PRODUCT SERVICES
# =========================================================

def get_products():

    return api_get("/products/")


def get_product(product_id):

    return api_get(
        f"/products/{product_id}"
    )


def search_products(
    name="",
    max_price=100000
):

    return api_get(
        "/products/search/",
        {
            "name": name,
            "max_price": max_price
        }
    )


def check_inventory(product_id):

    return api_get(
        f"/products/inventory/{product_id}"
    )


# =========================================================
# CART SERVICES
# =========================================================

def get_cart():

    return api_get("/cart/")


def add_product(
    product_id,
    quantity=1
):

    return api_post(
        "/cart/add",
        {
            "product_id": product_id,
            "quantity": quantity
        }
    )


def remove_product(product_id):

    return api_delete(
        f"/cart/remove/{product_id}"
    )


def update_quantity(
    product_id,
    quantity
):

    return api_put(
        f"/cart/update/{product_id}",
        {
            "quantity": quantity
        }
    )


def clear_cart():

    return api_delete(
        "/cart/clear"
    )


# =========================================================
# ORDER SERVICES
# =========================================================

def create_order():

    return api_post(
        "/orders/create"
    )


# =========================================================
# HELPERS
# =========================================================

def product_name(product):

    return (
        product.get("name")
        or product.get("product_name")
        or f"Product #{product.get('id')}"
    )


def format_price(value):

    return f"₹{float(value):,.2f}"


def find_product_by_name(
    products,
    text
):

    text = text.lower()

    # Exact/full product name first

    for product in products:

        name = product_name(
            product
        ).lower()

        if name in text:
            return product

    # Partial word matching

    words = [
        word
        for word in re.findall(
            r"[a-zA-Z0-9]+",
            text
        )
        if len(word) >= 3
    ]

    best_product = None
    best_score = 0

    for product in products:

        name = product_name(
            product
        ).lower()

        score = sum(
            1
            for word in words
            if word in name
        )

        if score > best_score:

            best_score = score
            best_product = product

    return best_product


def extract_price(text):

    patterns = [

        r"(?:under|below|less than|within|max|maximum)\s*₹?\s*([\d,]+)",

        r"₹\s*([\d,]+)",

        r"rs\.?\s*([\d,]+)",

        r"inr\s*([\d,]+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text.lower()
        )

        if match:

            try:

                return float(
                    match.group(1)
                    .replace(",", "")
                )

            except ValueError:
                pass

    return None


def extract_quantity(text):

    patterns = [

        r"make\s+it\s+(\d+)",

        r"change\s+(?:it|quantity)\s+to\s+(\d+)",

        r"set\s+(?:quantity|it)\s+to\s+(\d+)",

        r"quantity\s+(?:to|=)\s*(\d+)",

        r"(\d+)\s*(?:items?|pieces?|units?)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text.lower()
        )

        if match:

            return int(
                match.group(1)
            )

    return None


# =========================================================
# CATEGORY DETECTION
# =========================================================

CATEGORY_KEYWORDS = {

    "laptop": [
        "laptop",
        "laptops",
        "notebook"
    ],

    "phone": [
        "phone",
        "phones",
        "mobile",
        "mobiles",
        "smartphone"
    ],

    "tablet": [
        "tablet",
        "tablets",
        "ipad"
    ],

    "monitor": [
        "monitor",
        "monitors",
        "display"
    ],

    "keyboard": [
        "keyboard",
        "keyboards"
    ],

    "mouse": [
        "mouse",
        "mice"
    ],

    "headphone": [
        "headphone",
        "headphones",
        "earphone",
        "earphones",
        "headset"
    ]
}


def detect_category(text):

    text = text.lower()

    for category, words in CATEGORY_KEYWORDS.items():

        for word in words:

            if word in text:

                return category

    return ""


# =========================================================
# GEMINI INTENT ANALYSIS
# =========================================================

def analyze_with_gemini(message):

    if not gemini_client:

        return None

    prompt = f"""
You are the intelligence layer of CommercePilot AI,
an agentic shopping assistant.

Analyze the user's shopping request.

Return ONLY valid JSON.

Possible intents:

search
recommend
add
remove
cart
quantity
compare
inventory
checkout
clear_cart
help

Extract:

intent
category
product_name
budget
quantity
reference
comparison
confidence

User request:
{message}

Example:

{{
  "intent": "search",
  "category": "laptop",
  "product_name": "",
  "budget": 60000,
  "quantity": null,
  "reference": null,
  "comparison": null,
  "confidence": 0.95
}}
"""

    try:

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        text = re.sub(
            r"^```json",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"^```",
            "",
            text
        )

        text = re.sub(
            r"```$",
            "",
            text
        )

        return json.loads(
            text.strip()
        )

    except Exception:

        return None


# =========================================================
# SHOW CART
# =========================================================

def handle_show_cart():

    cart = get_cart()

    if not cart:

        return {
            "type": "cart",
            "message": "Your cart is empty.",
            "items": [],
            "total": 0,
            "actions": []
        }

    items = []
    total = 0

    for item in cart:

        quantity = int(
            item.get(
                "quantity",
                0
            )
        )

        item_total = float(
            item.get(
                "total_price",
                0
            )
        )

        total += item_total

        try:

            product = get_product(
                item["product_id"]
            )

            name = product_name(
                product
            )

        except Exception:

            name = (
                item.get(
                    "product_name"
                )
                or
                f"Product #{item['product_id']}"
            )

        items.append({

            "product_id":
                item["product_id"],

            "product":
                name,

            "quantity":
                quantity,

            "total_price":
                item_total
        })

    return {

        "type": "cart",

        "message":
            f"You have {len(items)} "
            f"product(s) in your cart.",

        "items":
            items,

        "total":
            total,

        "actions": [
            "checkout",
            "clear cart"
        ]
    }


# =========================================================
# SEARCH
# =========================================================

def handle_search(
    text,
    gemini_data=None
):

    budget = extract_price(
        text
    )

    category = detect_category(
        text
    )

    if gemini_data:

        if gemini_data.get(
            "budget"
        ):

            try:

                budget = float(
                    gemini_data[
                        "budget"
                    ]
                )

            except Exception:
                pass

        if (
            gemini_data.get(
                "category"
            )
        ):

            category = gemini_data[
                "category"
            ]

    products = search_products(

        name=category,

        max_price=budget
        if budget
        else 100000
    )

    assistant_state[
        "last_products"
    ] = products

    assistant_state[
        "last_intent"
    ] = "search"

    if not products:

        if budget:

            return {

                "type":
                    "products",

                "message":
                    f"I couldn't find any "
                    f"matching products under "
                    f"{format_price(budget)}.",

                "products": [],

                "actions": []
            }

        return {

            "type":
                "products",

            "message":
                "I couldn't find matching products.",

            "products": [],

            "actions": []
        }

    if budget:

        message = (
            f"I found {len(products)} "
            f"good option(s) within "
            f"{format_price(budget)}."
        )

    else:

        message = (
            f"I found {len(products)} "
            f"{category or 'product'} "
            f"option(s) for you."
        )

    return {

        "type":
            "products",

        "message":
            message,

        "products":
            products[:10],

        "actions": [
            "add first",
            "compare"
        ]
    }


# =========================================================
# ADD PRODUCT
# =========================================================

def handle_add(
    text,
    gemini_data=None
):

    products = get_products()

    # -----------------------------------------
    # Reference: first / second / third
    # -----------------------------------------

    last_products = assistant_state.get(
        "last_products",
        []
    )

    reference = None

    if gemini_data:

        reference = gemini_data.get(
            "reference"
        )

    if "first" in text:
        reference = "first"

    elif "second" in text:
        reference = "second"

    elif "third" in text:
        reference = "third"

    if reference:

        indexes = {
            "first": 0,
            "second": 1,
            "third": 2
        }

        index = indexes.get(
            reference
        )

        if (
            index is not None
            and index < len(last_products)
        ):

            product = last_products[
                index
            ]

        else:

            return {

                "type":
                    "question",

                "message":
                    "That product isn't available "
                    "in the latest results.",

                "actions": []
            }

    else:

        product = find_product_by_name(
            products,
            text
        )

    if not product:

        return {

            "type":
                "question",

            "message":
                "Which product would you like "
                "to add to your cart?",

            "actions": []
        }

    quantity = (
        extract_quantity(text)
        or 1
    )

    if gemini_data:

        try:

            if gemini_data.get(
                "quantity"
            ):

                quantity = int(
                    gemini_data[
                        "quantity"
                    ]
                )

        except Exception:
            pass

    result = add_product(
        product["id"],
        quantity
    )

    if result.get(
        "error"
    ):

        return {

            "type":
                "error",

            "message":
                result["error"],

            "actions": []
        }

    assistant_state[
        "selected_product"
    ] = product

    assistant_state[
        "last_intent"
    ] = "add"

    return {

        "type":
            "action",

        "message":
            f"{product['name']} added "
            f"to your cart.",

        "product":
            product,

        "quantity":
            quantity,

        "actions": [
            "show my cart",
            "checkout"
        ]
    }


# =========================================================
# CHANGE QUANTITY
# =========================================================

def handle_quantity(text):

    quantity = extract_quantity(
        text
    )

    if quantity is None:

        return {

            "type":
                "question",

            "message":
                "What quantity would you like?",

            "actions": []
        }

    cart = get_cart()

    if not cart:

        return {

            "type":
                "cart",

            "message":
                "Your cart is empty.",

            "actions": []
        }

    products = get_products()

    target = None

    named_product = find_product_by_name(
        products,
        text
    )

    if named_product:

        for item in cart:

            if (
                item["product_id"]
                ==
                named_product["id"]
            ):

                target = item
                break

    if target is None:

        selected = assistant_state.get(
            "selected_product"
        )

        if selected:

            for item in cart:

                if (
                    item["product_id"]
                    ==
                    selected["id"]
                ):

                    target = item
                    break

    if (
        target is None
        and len(cart) == 1
    ):

        target = cart[0]

    if target is None:

        return {

            "type":
                "question",

            "message":
                "Which cart item would "
                "you like to change?",

            "actions": []
        }

    product = get_product(
        target["product_id"]
    )

    result = update_quantity(
        target["product_id"],
        quantity
    )

    if result.get(
        "error"
    ):

        return {

            "type":
                "error",

            "message":
                result["error"],

            "actions": []
        }

    assistant_state[
        "selected_product"
    ] = product

    return {

        "type":
            "action",

        "message":
            f"{product['name']} quantity "
            f"updated to {quantity}.",

        "product":
            product,

        "quantity":
            quantity,

        "actions": [
            "show my cart",
            "checkout"
        ]
    }


# =========================================================
# REMOVE PRODUCT
# =========================================================

def handle_remove(text):

    products = get_products()

    product = find_product_by_name(
        products,
        text
    )

    if not product:

        return {

            "type":
                "question",

            "message":
                "Which product would you "
                "like to remove?",

            "actions": []
        }

    result = remove_product(
        product["id"]
    )

    return {

        "type":
            "action",

        "message":
            result.get(
                "message",
                f"{product['name']} removed "
                f"from your cart."
            ),

        "actions": [
            "show my cart"
        ]
    }


# =========================================================
# CLEAR CART
# =========================================================

def handle_clear():

    result = clear_cart()

    assistant_state[
        "selected_product"
    ] = None

    return {

        "type":
            "action",

        "message":
            result.get(
                "message",
                "Your cart has been cleared."
            ),

        "actions": []
    }


# =========================================================
# COMPARE
# =========================================================

def handle_compare(text):

    products = assistant_state.get(
        "last_products",
        []
    )

    if len(products) < 2:

        return {

            "type":
                "question",

            "message":
                "Please search for at least "
                "two products before comparing.",

            "actions": []
        }

    first = None
    second = None

    if (
        "first" in text
        and "second" in text
    ):

        first = products[0]
        second = products[1]

    else:

        first = find_product_by_name(
            products,
            text
        )

        if first:

            remaining = [

                p for p in products

                if p["id"]
                != first["id"]
            ]

            second = find_product_by_name(
                remaining,
                text
            )

    if not first or not second:

        return {

            "type":
                "question",

            "message":
                "Say: Compare the first and second.",

            "actions": []
        }

    comparison = {

        "product_1": {

            "id":
                first["id"],

            "name":
                first["name"],

            "price":
                first.get("price"),

            "rating":
                first.get("rating"),

            "stock":
                first.get("stock"),

            "category":
                first.get("category")
        },

        "product_2": {

            "id":
                second["id"],

            "name":
                second["name"],

            "price":
                second.get("price"),

            "rating":
                second.get("rating"),

            "stock":
                second.get("stock"),

            "category":
                second.get("category")
        }
    }

    return {

        "type":
            "comparison",

        "message":
            f"Here's a comparison of "
            f"{first['name']} and "
            f"{second['name']}.",

        "comparison":
            comparison,

        "actions": [
            "add first",
            "add second"
        ]
    }


# =========================================================
# INVENTORY
# =========================================================

def handle_inventory(text):

    products = get_products()

    product = find_product_by_name(
        products,
        text
    )

    if not product:

        selected = assistant_state.get(
            "selected_product"
        )

        if selected:
            product = selected

    if not product:

        return {

            "type":
                "question",

            "message":
                "Which product should I check?",

            "actions": []
        }

    result = check_inventory(
        product["id"]
    )

    return {

        "type":
            "inventory",

        "message":
            f"{product['name']} has "
            f"{result.get('stock', 0)} "
            f"item(s) in stock.",

        "inventory":
            result,

        "actions": [
            "add to cart"
        ]
    }


# =========================================================
# CHECKOUT
# =========================================================

def handle_checkout():

    cart = get_cart()

    if not cart:

        return {

            "type":
                "checkout",

            "message":
                "Your cart is empty. Add products "
                "before checkout.",

            "total":
                0,

            "actions": []
        }

    total = sum(

        float(
            item.get(
                "total_price",
                0
            )
        )

        for item in cart
    )

    return {

        "type":
            "checkout",

        "message":
            f"Your order total is "
            f"{format_price(total)}. "
            f"You can proceed to secure checkout.",

        "total":
            total,

        "actions": [
            "proceed to checkout"
        ]
    }


# =========================================================
# CREATE ORDER
# =========================================================

def handle_create_order():

    result = create_order()

    if result.get(
        "error"
    ):

        return {

            "type":
                "error",

            "message":
                result["error"],

            "actions": []
        }

    return {

        "type":
            "order",

        "message":
            "Your order has been created "
            "successfully.",

        "order":
            result,

        "actions": [
            "pay with Razorpay"
        ]
    }


# =========================================================
# HELP
# =========================================================

def handle_help():

    return {

        "type":
            "help",

        "message":
            "Hi! I can help you shop.\n\n"
            "Try asking:\n"
            "• Find laptops\n"
            "• Find laptops under ₹60,000\n"
            "• Recommend a laptop for AI/ML\n"
            "• Add the first one to my cart\n"
            "• Make it 2\n"
            "• Show my cart\n"
            "• Compare the first and second\n"
            "• Check Acer Aspire 5 stock\n"
            "• Remove Acer Aspire 5 from cart\n"
            "• Checkout",

        "actions": []
    }


# =========================================================
# MAIN AGENT
# =========================================================

@router.post("/chat")
def agent_chat(
    message: str
):

    text = message.lower().strip()

    if not text:

        return {

            "type":
                "help",

            "message":
                "Please tell me what you'd "
                "like to shop for.",

            "actions": []
        }

    try:

        # =================================================
        # GEMINI UNDERSTANDING
        # =================================================

        gemini_data = analyze_with_gemini(
            message
        )

        # =================================================
        # CART
        # =================================================

        if (
            text in [
                "cart",
                "show cart",
                "show my cart",
                "view cart",
                "view my cart"
            ]
            or
            "what is in my cart" in text
        ):

            return handle_show_cart()

        # =================================================
        # CLEAR CART
        # =================================================

        if (
            "clear cart" in text
            or "clear my cart" in text
            or "empty cart" in text
            or "empty my cart" in text
            or "remove everything" in text
        ):

            return handle_clear()

        # =================================================
        # CHECKOUT
        # =================================================

        if (
            text == "checkout"
            or
            "proceed to checkout" in text
            or
            "buy everything" in text
        ):

            return handle_checkout()

        # =================================================
        # CREATE ORDER
        # =================================================

        if (
            "place order" in text
            or
            "create order" in text
            or
            "confirm order" in text
        ):

            return handle_create_order()

        # =================================================
        # COMPARE
        # =================================================

        if "compare" in text:

            return handle_compare(
                text
            )

        # =================================================
        # QUANTITY
        # =================================================

        if (
            "make it" in text
            or
            "change quantity" in text
            or
            "set quantity" in text
            or
            "quantity to" in text
        ):

            return handle_quantity(
                text
            )

        # =================================================
        # REMOVE
        # =================================================

        if (
            "remove" in text
            and "cart" in text
        ):

            return handle_remove(
                text
            )

        # =================================================
        # ADD
        # =================================================

        if (
            "add" in text
            or
            (
                gemini_data
                and
                gemini_data.get(
                    "intent"
                ) == "add"
            )
        ):

            return handle_add(
                text,
                gemini_data
            )

        # =================================================
        # INVENTORY
        # =================================================

        if (
            "stock" in text
            or
            "inventory" in text
            or
            "available" in text
        ):

            return handle_inventory(
                text
            )

        # =================================================
        # SEARCH / RECOMMEND
        # =================================================

        search_words = [

            "find",
            "search",
            "show me",
            "looking for",
            "want",
            "need",
            "recommend",
            "suggest",
            "best",
            "laptop",
            "phone",
            "tablet",
            "computer",
            "monitor",
            "keyboard",
            "mouse",
            "headphone"
        ]

        if (
            any(
                word in text
                for word in search_words
            )
            or
            (
                gemini_data
                and
                gemini_data.get(
                    "intent"
                )
                in [
                    "search",
                    "recommend"
                ]
            )
        ):

            return handle_search(
                text,
                gemini_data
            )

        # =================================================
        # FALLBACK HELP
        # =================================================

        return handle_help()

    except requests.exceptions.RequestException as error:

        return {

            "type":
                "error",

            "message":
                "I couldn't connect to the "
                "CommercePilot backend. "
                "Please make sure the backend "
                "is running.",

            "details":
                str(error),

            "actions": []
        }

    except Exception as error:

        return {

            "type":
                "error",

            "message":
                "Something went wrong while "
                "processing your shopping request.",

            "details":
                str(error),

            "actions": []
        }