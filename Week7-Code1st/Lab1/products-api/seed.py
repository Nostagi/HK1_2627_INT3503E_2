
import random

from app import create_app
from src.handlers.config import DefaultConfig
from src.extensions import db

# Models
from src.models.product import Product
from src.models.order import Order, OrderItem


CATEGORIES = [
    "Electronics",
    "Books",
    "Clothing",
    "Home",
    "Toys",
]

BASE_NAMES = [
    "Wireless Mouse",
    "Mechanical Keyboard",
    "USB-C Hub",
    '27" Monitor',
    "Noise-Cancel Headphone",
    "Python Cookbook",
    "Clean Code",
    "Atomic Habits",
    "Cotton T-Shirt",
    "Running Shoes",
    "Coffee Mug",
    "LED Desk Lamp",
    "Yoga Mat",
    "LEGO Set",
    "Board Game Catan",
    "Bluetooth Speaker",
]


def seed_products(n: int = 40):
    products = []

    for i in range(1, n + 1):
        product = Product(
            sku=f"SKU-{i:04d}",
            name=f"{random.choice(BASE_NAMES)} #{i}",
            description=f"Mô tả sản phẩm mẫu #{i}",
            category=random.choice(CATEGORIES),
            price_cents=random.randint(990, 999_900),
            qty_in_stock=random.choice(
                [0, 0, 0, random.randint(1, 500)]
            ),
        )

        products.append(product)

    db.session.add_all(products)
    db.session.flush()

    return products


def seed_orders(products, n: int = 10):
    orders = []

    available_products = [
        p for p in products
        if not p.archived
    ]

    if not available_products:
        return orders

    for _ in range(n):
        order = Order()

        selected_products = random.sample(
            available_products,
            k=random.randint(
                1,
                min(4, len(available_products)),
            ),
        )

        for product in selected_products:
            item = OrderItem(
                product=product,
                quantity=random.randint(1, 5),
                unit_price_cents=product.price_cents,
            )

            order.items.append(item)

        orders.append(order)

    db.session.add_all(orders)

    return orders


def seed(n: int = 40, order_count: int = 10):
    app = create_app(DefaultConfig)

    with app.app_context():
        try:
            # XÓA TOÀN BỘ DATABASE CŨ
            print("Đang xóa database cũ...")
            db.drop_all()

            # TẠO DATABASE MỚI
            print("Đang tạo database mới...")
            db.create_all()

            # SEED PRODUCTS
            products = seed_products(n)

            # SEED ORDERS + ORDER ITEMS
            orders = seed_orders(
                products,
                order_count,
            )

            # COMMIT
            db.session.commit()

            print("Seed thành công!")
            print(f"Products: {len(products)}")
            print(f"Orders: {len(orders)}")

            item_count = sum(
                len(order.items)
                for order in orders
            )

            print(f"OrderItems: {item_count}")

        except Exception:
            db.session.rollback()
            raise

    return app


if __name__ == "__main__":
    app = seed()

    LOCALHOST = {
        "host": "127.0.0.1",
        "port": 5000,
        "debug": True,
    }

    app.run(**LOCALHOST)
