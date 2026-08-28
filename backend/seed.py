from database import SessionLocal, engine, Base
from models import Product

Base.metadata.create_all(bind=engine)

db = SessionLocal()

products = [
    Product(
        name="Acer Aspire 5",
        category="Laptop",
        price=55000,
        description="15.6 inch laptop with Intel i5, 16GB RAM and 512GB SSD",
        stock=10,
        rating=4.2
    ),
    Product(
        name="ASUS Vivobook 15",
        category="Laptop",
        price=62000,
        description="15.6 inch laptop with Intel i5, 16GB RAM and 512GB SSD",
        stock=8,
        rating=4.4
    ),
    Product(
        name="Lenovo LOQ",
        category="Laptop",
        price=70000,
        description="Gaming laptop with Intel i5, 16GB RAM and RTX 3050",
        stock=5,
        rating=4.6
    ),
    Product(
        name="HP Pavilion",
        category="Laptop",
        price=58000,
        description="Laptop with Ryzen 5, 16GB RAM and 512GB SSD",
        stock=12,
        rating=4.3
    ),
]

db.add_all(products)
db.commit()
db.close()

print("Products added successfully!")