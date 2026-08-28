from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Cart, Order


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
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
# CREATE LOCAL COMMERCEPILOT ORDER
# =========================================================

@router.post("/create")
def create_order(
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # GET CART
    # -----------------------------------------------------

    cart_items = db.query(Cart).all()

    if not cart_items:

        return {
            "success": False,
            "error": "Cart is empty"
        }


    # -----------------------------------------------------
    # CALCULATE REAL ORDER TOTAL
    # -----------------------------------------------------

    total_amount = sum(
        float(item.total_price or 0)
        for item in cart_items
    )


    if total_amount <= 0:

        return {
            "success": False,
            "error": "Invalid order amount"
        }


    # -----------------------------------------------------
    # CREATE LOCAL ORDER
    # -----------------------------------------------------

    order = Order(

        total_amount=total_amount,

        status="created"

    )


    db.add(order)

    db.commit()

    db.refresh(order)


    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {

        "success": True,

        "message":
            "Order created successfully",

        "order_id":
            order.id,

        "total_amount":
            total_amount,

        "status":
            order.status

    }


# =========================================================
# GET ALL ORDERS
# =========================================================

@router.get("/")
def get_orders(
    db: Session = Depends(get_db)
):

    return db.query(Order).all()