from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Product, Cart

router = APIRouter(prefix="/cart", tags=["Cart"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ADD TO CART
@router.post("/add")
def add_to_cart(
    product_id: int,
    quantity: int = 1,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return {"error": "Product not found"}

    if quantity <= 0:
        return {"error": "Quantity must be greater than 0"}

    cart_item = db.query(Cart).filter(
        Cart.product_id == product_id
    ).first()

    if cart_item:
        new_quantity = cart_item.quantity + quantity

        if product.stock < new_quantity:
            return {"error": "Not enough stock"}

        cart_item.quantity = new_quantity
        cart_item.total_price = product.price * new_quantity

    else:
        if product.stock < quantity:
            return {"error": "Not enough stock"}

        cart_item = Cart(
            product_id=product_id,
            quantity=quantity,
            total_price=product.price * quantity
        )

        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Product added to cart",
        "product": product.name,
        "quantity": cart_item.quantity,
        "total_price": cart_item.total_price
    }


# VIEW CART
@router.get("/")
def get_cart(db: Session = Depends(get_db)):
    items = db.query(Cart).all()

    return items


# REMOVE PRODUCT FROM CART
@router.delete("/remove/{product_id}")
def remove_from_cart(
    product_id: int,
    db: Session = Depends(get_db)
):
    cart_item = db.query(Cart).filter(
        Cart.product_id == product_id
    ).first()

    if not cart_item:
        return {"error": "Product not found in cart"}

    db.delete(cart_item)
    db.commit()

    return {
        "message": "Product removed from cart",
        "product_id": product_id
    }


# UPDATE QUANTITY
@router.put("/update/{product_id}")
def update_cart_quantity(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):
    if quantity <= 0:
        return {"error": "Quantity must be greater than 0"}

    cart_item = db.query(Cart).filter(
        Cart.product_id == product_id
    ).first()

    if not cart_item:
        return {"error": "Product not found in cart"}

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        return {"error": "Product not found"}

    if product.stock < quantity:
        return {"error": "Not enough stock"}

    cart_item.quantity = quantity
    cart_item.total_price = product.price * quantity

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Cart quantity updated",
        "product": product.name,
        "quantity": cart_item.quantity,
        "total_price": cart_item.total_price
    }


# CLEAR CART
@router.delete("/clear")
def clear_cart(db: Session = Depends(get_db)):
    items = db.query(Cart).all()

    for item in items:
        db.delete(item)

    db.commit()

    return {
        "message": "Cart cleared successfully"
    }