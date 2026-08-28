from sqlalchemy import Column, Integer, String, Float
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String)
    price = Column(Float)
    description = Column(String)
    stock = Column(Integer)
    rating = Column(Float)


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)
    total_price = Column(Float)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    total_amount = Column(Float, nullable=False)

    status = Column(
        String,
        default="created"
    )

    # Razorpay information
    razorpay_order_id = Column(
        String,
        nullable=True
    )

    razorpay_payment_id = Column(
        String,
        nullable=True
    )

    razorpay_signature = Column(
        String,
        nullable=True
    )