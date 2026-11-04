import random

from app import create_app
from src.handlers.config import DefaultConfig
from src.extensions import db
from src.models.product import Product

CATEGORIES = ["Electronics", "Books", "Clothing", "Home", "Toys"]
BASE_NAMES = [
    "Wireless Mouse", "Mechanical Keyboard", "USB-C Hub", "27\" Monitor",
    "Noise-Cancel Headphone", "Python Cookbook", "Clean Code", "Atomic Habits",
    "Cotton T-Shirt", "Running Shoes", "Coffee Mug", "LED Desk Lamp",
    "Yoga Mat", "LEGO Set", "Board Game Catan", "Bluetooth Speaker",
]


def seed(n: int = 40):
    app = create_app(DefaultConfig)
    with app.app_context():
        db.create_all()
        if db.session.scalar(db.select(db.func.count()).select_from(Product)):
            print("DB đã có dữ liệu — bỏ qua seed.")
        else:
            for i in range(1, n + 1):
                p = Product(
                    sku=f"SKU-{i:04d}",
                    name=f"{random.choice(BASE_NAMES)} #{i}",
                    description=f"Mô tả sản phẩm mẫu #{i}",
                    category=random.choice(CATEGORIES),
                    price_cents=random.randint(990, 999_900),
                    qty_in_stock=random.choice([0, 0, 0, random.randint(1, 500)]),
                )
                db.session.add(p)
            db.session.commit()
            print(f"✔ Đã seed {n} products.")

    return app


if __name__ == "__main__":
    app = seed()

    LOCALHOST:dict = {
        "host" : "127.0.0.1",
        "port" : 5000,
        "debug" : True      # only for localhost3
    }

    app.run(**LOCALHOST)