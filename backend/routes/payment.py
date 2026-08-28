import os

import razorpay

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import SessionLocal
from models import Order


# =========================================================
# LOAD .ENV
# =========================================================

load_dotenv()


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/payment",
    tags=["Payment"]
)


# =========================================================
# DATABASE
# =========================================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# =========================================================
# RAZORPAY CONFIGURATION
# =========================================================

RAZORPAY_KEY_ID = os.getenv(
    "RAZORPAY_KEY_ID",
    ""
).strip()


RAZORPAY_KEY_SECRET = os.getenv(
    "RAZORPAY_KEY_SECRET",
    ""
).strip()


# =========================================================
# TEST MODE
# =========================================================

RAZORPAY_TEST_MODE = (
    os.getenv(
        "RAZORPAY_TEST_MODE",
        "true"
    )
    .strip()
    .lower()
    == "true"
)


# =========================================================
# TEST PAYMENT AMOUNT
# =========================================================

try:

    RAZORPAY_TEST_AMOUNT = float(
        os.getenv(
            "RAZORPAY_TEST_AMOUNT",
            "500"
        )
    )

except ValueError:

    RAZORPAY_TEST_AMOUNT = 500.0


# =========================================================
# CONFIGURATION VALIDATION
# =========================================================

print()
print("==========================================")
print("       COMMERCEPILOT RAZORPAY")
print("==========================================")

print(
    "TEST MODE:",
    RAZORPAY_TEST_MODE
)

print(
    "TEST PAYMENT AMOUNT: ₹",
    RAZORPAY_TEST_AMOUNT
)

if RAZORPAY_KEY_ID:

    print(
        "KEY TYPE:",
        (
            "TEST"
            if RAZORPAY_KEY_ID.startswith("rzp_test_")
            else "LIVE / OTHER"
        )
    )

    print(
        "KEY:",
        RAZORPAY_KEY_ID[:12] + "..."
    )

else:

    print(
        "WARNING: RAZORPAY_KEY_ID is missing."
    )


if not RAZORPAY_KEY_SECRET:

    print(
        "WARNING: RAZORPAY_KEY_SECRET is missing."
    )


print("==========================================")
print()


# =========================================================
# RAZORPAY CLIENT
# =========================================================

client = razorpay.Client(
    auth=(
        RAZORPAY_KEY_ID,
        RAZORPAY_KEY_SECRET
    )
)


# =========================================================
# GET LOCAL ORDER
# =========================================================

def get_order(
    order_id: int,
    db: Session
):

    return (
        db.query(Order)
        .filter(
            Order.id == order_id
        )
        .first()
    )


# =========================================================
# CALCULATE PAYMENT AMOUNT
# =========================================================

def get_payment_amount(
    real_order_amount: float
) -> float:

    """
    TEST MODE:
        Real order = ₹55,000
        Razorpay payment = ₹500

    LIVE MODE:
        Real order = ₹55,000
        Razorpay payment = ₹55,000
    """

    if RAZORPAY_TEST_MODE:

        return RAZORPAY_TEST_AMOUNT

    return real_order_amount


# =========================================================
# CREATE RAZORPAY ORDER
# =========================================================

@router.post("/create/{order_id}")
def create_payment(

    order_id: int,

    db: Session = Depends(get_db)

):

    # -----------------------------------------------------
    # FIND LOCAL ORDER
    # -----------------------------------------------------

    order = get_order(
        order_id,
        db
    )


    if not order:

        return {

            "success": False,

            "error":
                "Order not found"

        }


    # -----------------------------------------------------
    # GET REAL ORDER AMOUNT
    # -----------------------------------------------------

    try:

        real_amount = float(
            order.total_amount
        )

    except (
        TypeError,
        ValueError
    ):

        return {

            "success": False,

            "error":
                "Invalid order amount"

        }


    if real_amount <= 0:

        return {

            "success": False,

            "error":
                "Order amount must be greater than ₹0"

        }


    # -----------------------------------------------------
    # DETERMINE ACTUAL RAZORPAY PAYMENT AMOUNT
    # -----------------------------------------------------

    payment_amount = get_payment_amount(
        real_amount
    )


    if payment_amount <= 0:

        return {

            "success": False,

            "error":
                "Invalid Razorpay payment amount"

        }


    # -----------------------------------------------------
    # CONVERT RUPEES TO PAISE
    # -----------------------------------------------------

    amount_paise = int(
        round(
            payment_amount * 100
        )
    )


    if amount_paise < 100:

        return {

            "success": False,

            "error":
                "Razorpay payment amount must be at least ₹1"

        }


    # =====================================================
    # DEBUG
    # =====================================================

    print()
    print("========== RAZORPAY PAYMENT DEBUG ==========")

    print(
        "LOCAL ORDER ID:",
        order.id
    )

    print(
        "TEST MODE:",
        RAZORPAY_TEST_MODE
    )

    print(
        "TEST KEY:",
        (
            RAZORPAY_KEY_ID.startswith(
                "rzp_test_"
            )
            if RAZORPAY_KEY_ID
            else False
        )
    )

    print(
        "DISPLAY / REAL ORDER AMOUNT: ₹",
        real_amount
    )

    print(
        "RAZORPAY PAYMENT AMOUNT: ₹",
        payment_amount
    )

    print(
        "RAZORPAY AMOUNT IN PAISE:",
        amount_paise
    )

    print(
        "RAZORPAY KEY:",
        (
            RAZORPAY_KEY_ID[:12] + "..."
            if RAZORPAY_KEY_ID
            else "NOT CONFIGURED"
        )
    )

    print("============================================")
    print()


    # =====================================================
    # VALIDATE RAZORPAY CONFIGURATION
    # =====================================================

    if not RAZORPAY_KEY_ID:

        return {

            "success": False,

            "error":
                "Razorpay Key ID is not configured."

        }


    if not RAZORPAY_KEY_SECRET:

        return {

            "success": False,

            "error":
                "Razorpay Key Secret is not configured."

        }


    # =====================================================
    # EXISTING RAZORPAY ORDER
    # =====================================================

    if order.razorpay_order_id:

        print(
            "Existing Razorpay order found:",
            order.razorpay_order_id
        )

        print(
            "Creating a fresh Razorpay order "
            "to guarantee the correct TEST amount."
        )

        # -------------------------------------------------
        # IMPORTANT
        #
        # We intentionally do NOT reuse the old Razorpay
        # order because it may have been created for
        # ₹55,000 before TEST MODE was enabled.
        # -------------------------------------------------

        order.razorpay_order_id = None

        order.razorpay_payment_id = None

        order.razorpay_signature = None

        order.status = "created"

        db.commit()

        db.refresh(order)


    # =====================================================
    # CREATE NEW RAZORPAY ORDER
    # =====================================================

    try:

        razorpay_order = client.order.create({

            "amount":
                amount_paise,

            "currency":
                "INR",

            "receipt":
                f"commercepilot_{order.id}",

            "notes": {

                "commercepilot_order_id":
                    str(order.id),

                "real_order_amount":
                    str(real_amount),

                "payment_amount":
                    str(payment_amount),

                "test_mode":
                    str(
                        RAZORPAY_TEST_MODE
                    )

            }

        })


        # -------------------------------------------------
        # SAVE RAZORPAY ORDER ID
        # -------------------------------------------------

        order.razorpay_order_id = (
            razorpay_order["id"]
        )

        order.status = (
            "payment_pending"
        )


        db.commit()

        db.refresh(order)


        # =================================================
        # RESPONSE
        # =================================================

        return {

            "success": True,

            "message":
                "Razorpay order created successfully",

            "order_id":
                order.id,

            "razorpay_order_id":
                razorpay_order["id"],

            # REAL COMMERCE VALUE
            "order_amount":
                real_amount,

            # ACTUAL RAZORPAY VALUE
            "payment_amount":
                payment_amount,

            # RAZORPAY EXPECTS PAISE
            "amount_paise":
                amount_paise,

            "currency":
                "INR",

            "key_id":
                RAZORPAY_KEY_ID,

            "test_mode":
                RAZORPAY_TEST_MODE

        }


    # =====================================================
    # RAZORPAY BAD REQUEST
    # =====================================================

    except razorpay.errors.BadRequestError as error:

        print(
            "Razorpay BadRequestError:",
            str(error)
        )


        return {

            "success": False,

            "error":
                "Razorpay rejected the payment order.",

            "details":
                str(error),

            "order_amount":
                real_amount,

            "payment_amount":
                payment_amount,

            "amount_paise":
                amount_paise

        }


    # =====================================================
    # OTHER RAZORPAY ERROR
    # =====================================================

    except Exception as error:

        print(
            "Razorpay order creation error:",
            str(error)
        )


        return {

            "success": False,

            "error":
                "Unable to create Razorpay order.",

            "details":
                str(error)

        }


# =========================================================
# VERIFY PAYMENT
# =========================================================

@router.post("/verify")
def verify_payment(

    order_id: int,

    razorpay_payment_id: str,

    razorpay_order_id: str,

    razorpay_signature: str,

    db: Session = Depends(get_db)

):

    # -----------------------------------------------------
    # FIND LOCAL ORDER
    # -----------------------------------------------------

    order = get_order(
        order_id,
        db
    )


    if not order:

        return {

            "success": False,

            "error":
                "Order not found"

        }


    # -----------------------------------------------------
    # CHECK RAZORPAY ORDER
    # -----------------------------------------------------

    if not order.razorpay_order_id:

        return {

            "success": False,

            "error":
                "Razorpay order has not been created."

        }


    # -----------------------------------------------------
    # SECURITY CHECK
    # -----------------------------------------------------

    if (
        razorpay_order_id
        != order.razorpay_order_id
    ):

        return {

            "success": False,

            "error":
                "Razorpay order ID mismatch"

        }


    # -----------------------------------------------------
    # ALREADY PAID
    # -----------------------------------------------------

    if order.status == "paid":

        return {

            "success": True,

            "message":
                "Payment already verified",

            "order_id":
                order.id,

            "razorpay_order_id":
                order.razorpay_order_id,

            "razorpay_payment_id":
                order.razorpay_payment_id,

            "order_amount":
                float(
                    order.total_amount
                ),

            "payment_amount":
                get_payment_amount(
                    float(
                        order.total_amount
                    )
                ),

            "test_mode":
                RAZORPAY_TEST_MODE,

            "status":
                order.status

        }


    # =====================================================
    # VERIFY SIGNATURE
    # =====================================================

    try:

        client.utility.verify_payment_signature({

            "razorpay_order_id":
                order.razorpay_order_id,

            "razorpay_payment_id":
                razorpay_payment_id,

            "razorpay_signature":
                razorpay_signature

        })


        # -------------------------------------------------
        # PAYMENT VERIFIED
        # -------------------------------------------------

        order.status = "paid"

        order.razorpay_payment_id = (
            razorpay_payment_id
        )

        order.razorpay_signature = (
            razorpay_signature
        )


        db.commit()

        db.refresh(order)


        # -------------------------------------------------
        # SUCCESS RESPONSE
        # -------------------------------------------------

        return {

            "success": True,

            "message":
                "Payment verified successfully",

            "order_id":
                order.id,

            "razorpay_order_id":
                order.razorpay_order_id,

            "razorpay_payment_id":
                order.razorpay_payment_id,

            # ORIGINAL PRODUCT/ORDER VALUE
            "order_amount":
                float(
                    order.total_amount
                ),

            # ACTUAL TEST CHARGE
            "payment_amount":
                get_payment_amount(
                    float(
                        order.total_amount
                    )
                ),

            "test_mode":
                RAZORPAY_TEST_MODE,

            "status":
                order.status

        }


    # =====================================================
    # INVALID SIGNATURE
    # =====================================================

    except razorpay.errors.SignatureVerificationError:

        order.status = (
            "payment_failed"
        )

        db.commit()


        return {

            "success": False,

            "error":
                "Payment signature verification failed"

        }


    # =====================================================
    # OTHER ERROR
    # =====================================================

    except Exception as error:

        print(
            "Payment verification error:",
            str(error)
        )


        return {

            "success": False,

            "error":
                str(error)

        }


# =========================================================
# PAYMENT STATUS
# =========================================================

@router.get("/status/{order_id}")
def payment_status(

    order_id: int,

    db: Session = Depends(get_db)

):

    order = get_order(
        order_id,
        db
    )


    if not order:

        return {

            "success": False,

            "error":
                "Order not found"

        }


    real_amount = float(
        order.total_amount
    )


    payment_amount = get_payment_amount(
        real_amount
    )


    return {

        "success": True,

        "order_id":
            order.id,

        "status":
            order.status,

        "order_amount":
            real_amount,

        "payment_amount":
            payment_amount,

        "razorpay_order_id":
            order.razorpay_order_id,

        "razorpay_payment_id":
            order.razorpay_payment_id,

        "test_mode":
            RAZORPAY_TEST_MODE

    }