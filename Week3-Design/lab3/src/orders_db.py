from pathlib import Path
import json
import sqlite3


DB_PATH = Path(__file__).resolve().parent / "orders.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(seed=True):
    """Create the SQLite file/table and optionally insert example orders."""
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                cart TEXT NOT NULL
            )
            """
        )

        if seed:
            count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            if count == 0:
                seed_orders(conn)

        conn.commit()
    finally:
        conn.close()


def seed_orders(conn):
    """Example fake data. cart is stored as JSON text."""
    products = [
        ["keyboard", "mouse"],
        ["laptop", "mouse", "usb-c-cable"],
        ["monitor"],
        ["headset", "webcam"],
        ["keyboard", "desk-mat"],
        ["mouse", "usb-c-cable"],
        ["laptop"],
        ["monitor", "hdmi-cable"],
        ["headset"],
        ["keyboard", "mouse", "headset"],
        ["webcam", "usb-c-cable"],
        ["desk-mat"],
    ]

    statuses = ["pending", "paid", "shipped", "cancelled"]

    rows = []
    for order_id in range(1, 51):
        rows.append(
            {
                "order_id" : order_id,
                "customer_id": 1000 + ((order_id - 1) % 8),
                "status": statuses[(order_id - 1) % len(statuses)],
                "cart": json.dumps(products[(order_id - 1) % len(products)]),
            }
        )

    conn.executemany(
        """
        INSERT INTO orders (id, customer_id, status, cart)
        VALUES (:order_id, :customer_id, :status, :cart)
        """,
        rows,
    )

if __name__ == "__main__":
    init_db(seed=True)
    print("SQLite database initialized: orders.db")
