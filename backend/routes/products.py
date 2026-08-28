from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import SessionLocal
from models import Product

router = APIRouter(prefix="/products", tags=["Products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@router.get("/search/")
def search_products(
    name: str = "",
    max_price: float = 100000,
    db: Session = Depends(get_db)
):
    products = db.query(Product).filter(
        or_(
            Product.name.ilike(f"%{name}%"),
            Product.description.ilike(f"%{name}%")
        ),
        Product.price <= max_price
    ).all()

    return products


@router.get("/inventory/{product_id}")
def check_inventory(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return {"error": "Product not found"}

    return {
        "product_id": product.id,
        "product_name": product.name,
        "stock": product.stock,
        "available": product.stock > 0
    }


@router.get("/compare/")
def compare_products(
    product1: int,
    product2: int,
    db: Session = Depends(get_db)
):
    first = db.query(Product).filter(Product.id == product1).first()
    second = db.query(Product).filter(Product.id == product2).first()

    if not first or not second:
        return {"error": "One or both products not found"}

    return {
        "product_1": first,
        "product_2": second
    }


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return {"error": "Product not found"}

    return product