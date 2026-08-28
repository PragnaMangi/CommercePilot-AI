
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import inspect, text

from database import engine, Base

from routes.products import router as product_router
from routes.cart import router as cart_router
from routes.orders import router as order_router
from routes.payment import router as payment_router

from agent_api import router as agent_router


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

Base.metadata.create_all(bind=engine)


def migrate_database():

    inspector = inspect(engine)

    tables = inspector.get_table_names()

    if "orders" not in tables:
        return

    columns = [
        column["name"]
        for column in inspector.get_columns("orders")
    ]

    new_columns = {
        "razorpay_order_id": "VARCHAR",
        "razorpay_payment_id": "VARCHAR",
        "razorpay_signature": "VARCHAR"
    }

    with engine.begin() as connection:

        for column_name, column_type in new_columns.items():

            if column_name not in columns:

                connection.execute(
                    text(
                        f"ALTER TABLE orders "
                        f"ADD COLUMN {column_name} "
                        f"{column_type}"
                    )
                )


migrate_database()


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="CommercePilot AI",
    description=(
        "Agentic AI Commerce Platform "
        "with Gemini and Razorpay"
    ),
    version="1.0.0"
)


# =========================================================
# CORS CONFIGURATION
# =========================================================
#
# The frontend may be opened using:
#
# http://localhost:5500
# http://127.0.0.1:5500
# http://localhost:5501
# http://127.0.0.1:5501
# http://localhost:3000
# http://127.0.0.1:3000
# http://localhost:8080
# http://127.0.0.1:8080
#
# FastAPI requires the exact origin to be allowed.
# =========================================================

allowed_origins = [

    # VS Code Live Server
    "http://localhost:5500",
    "http://127.0.0.1:5500",

    "http://localhost:5501",
    "http://127.0.0.1:5501",

    # Common development ports
    "http://localhost:3000",
    "http://127.0.0.1:3000",

    "http://localhost:5173",
    "http://127.0.0.1:5173",

    "http://localhost:8080",
    "http://127.0.0.1:8080",

    # Direct localhost
    "http://localhost",
    "http://127.0.0.1",

]


app.add_middleware(

    CORSMiddleware,

    allow_origins=allowed_origins,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)


# =========================================================
# ROUTES
# =========================================================

app.include_router(
    product_router
)

app.include_router(
    cart_router
)

app.include_router(
    order_router
)

app.include_router(
    payment_router
)

app.include_router(
    agent_router
)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {

        "message":
            "CommercePilot AI Backend Running",

        "version":
            "1.0.0",

        "features": [

            "AI Shopping Agent",

            "Product Search",

            "Cart Management",

            "Product Comparison",

            "Inventory",

            "Order Management",

            "Razorpay Checkout",

            "Payment Verification"

        ]

    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {

        "status":
            "healthy",

        "service":
            "CommercePilot AI"

    }


# =========================================================
# DEBUG ENDPOINT
# =========================================================

@app.get("/debug")

def debug():

    return {

        "backend":
            "online",

        "api":
            "http://127.0.0.1:8000",

        "cors":
            "enabled",

        "allowed_origins":
            allowed_origins

    }

