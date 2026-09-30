"""
Module quản lý đơn hàng (order) dùng SQLite thuần (không ORM).

Schema:
    orders(id, price, currency)
    order_items(id, order_id, book_id, title, price, quantity)
"""

import sqlite3
from contextlib import contextmanager

DB_PATH = "orders.db"


# ---------------------------------------------------------------------------
# Kết nối & khởi tạo
# ---------------------------------------------------------------------------

@contextmanager
def _db():
    """Mở connection, tự commit/rollback, luôn đóng sau khi dùng."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str | None = None) -> None:
    """Tạo bảng nếu chưa có. Gọi 1 lần khi khởi động.

    Lưu ý: db_path phải là đường dẫn file, KHÔNG dùng ':memory:'
    vì mỗi lần _db() mở connection mới sẽ mất dữ liệu in-memory.
    """
    global DB_PATH
    if db_path:
        DB_PATH = db_path

    with _db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                price    REAL    NOT NULL DEFAULT 0,
                currency TEXT    NOT NULL DEFAULT 'USD'
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                book_id  INTEGER NOT NULL,
                title    TEXT    NOT NULL,
                price    REAL    NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1
            );

            CREATE INDEX IF NOT EXISTS idx_items_order ON order_items(order_id);
            CREATE INDEX IF NOT EXISTS idx_items_book  ON order_items(book_id);
            """
        )


# ---------------------------------------------------------------------------
# Helpers nội bộ
# ---------------------------------------------------------------------------

def _row_to_order(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    """Chuyển 1 row `orders` + các row `order_items` thành dict hoàn chỉnh."""
    items = conn.execute(
        "SELECT book_id, title, price, quantity "
        "FROM order_items WHERE order_id = ? ORDER BY id",
        (row["id"],),
    ).fetchall()
    return {
        "id": row["id"],
        "items": [dict(i) for i in items],
        "price": row["price"],
        "currency": row["currency"],
    }


def _insert_items(conn: sqlite3.Connection, order_id: int, items: list[dict]) -> None:
    conn.executemany(
        "INSERT INTO order_items (order_id, book_id, title, price, quantity) "
        "VALUES (?, ?, ?, ?, ?)",
        [
            (order_id, it["book_id"], it["title"], it["price"], it.get("quantity", 1))
            for it in items
        ],
    )


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def get_all_orders() -> list[dict]:
    with _db() as conn:
        rows = conn.execute("SELECT * FROM orders ORDER BY id").fetchall()
        return [_row_to_order(conn, r) for r in rows]


def find_by_id(oid: int):
    """Trả về (id, order) hoặc (None, None) nếu không tìm thấy."""
    with _db() as conn:
        row = conn.execute("SELECT * FROM orders WHERE id = ?", (oid,)).fetchone()
        if row is None:
            return None, None
        return oid, _row_to_order(conn, row)


def create_order(new_order: dict) -> dict:
    items = new_order.get("items", [])
    # Nếu client không truyền price, tự tính từ items
    price = new_order.get(
        "price",
        sum(it["price"] * it.get("quantity", 1) for it in items),
    )
    currency = new_order.get("currency", "USD")

    with _db() as conn:
        cur = conn.execute(
            "INSERT INTO orders (price, currency) VALUES (?, ?)",
            (price, currency),
        )
        oid = cur.lastrowid
        _insert_items(conn, oid, items)

        row = conn.execute("SELECT * FROM orders WHERE id = ?", (oid,)).fetchone()
        return _row_to_order(conn, row)


def update_order(oid: int, new_data: dict, replacement: bool = False) -> dict | None:
    """Cập nhật order.

    - replacement=True : thay toàn bộ (kể cả items).
    - replacement=False: chỉ cập nhật các field có trong new_data.
    Trả về order sau khi update, hoặc None nếu id không tồn tại.
    """
    with _db() as conn:
        row = conn.execute("SELECT * FROM orders WHERE id = ?", (oid,)).fetchone()
        if row is None:
            return None

        if replacement:
            conn.execute(
                "UPDATE orders SET price = ?, currency = ? WHERE id = ?",
                (new_data.get("price", 0), new_data.get("currency", "USD"), oid),
            )
            conn.execute("DELETE FROM order_items WHERE order_id = ?", (oid,))
            _insert_items(conn, oid, new_data.get("items", []))
        else:
            if "price" in new_data:
                conn.execute(
                    "UPDATE orders SET price = ? WHERE id = ?", (new_data["price"], oid)
                )
            if "currency" in new_data:
                conn.execute(
                    "UPDATE orders SET currency = ? WHERE id = ?",
                    (new_data["currency"], oid),
                )
            if "items" in new_data:
                conn.execute("DELETE FROM order_items WHERE order_id = ?", (oid,))
                _insert_items(conn, oid, new_data["items"])

        row = conn.execute("SELECT * FROM orders WHERE id = ?", (oid,)).fetchone()
        return _row_to_order(conn, row)


def delete_order(oid: int) -> bool:
    """Xoá order + items (nhờ ON DELETE CASCADE). Trả True nếu có xoá."""
    with _db() as conn:
        cur = conn.execute("DELETE FROM orders WHERE id = ?", (oid,))
        return cur.rowcount > 0


def get_order(query: dict) -> list[dict]:
    """Lọc order theo nhiều tiêu chí (kết hợp bằng AND):

    - book_id   : đơn có chứa sách này (JOIN order_items)
    - currency  : đơn vị tiền tệ (không phân biệt hoa/thường)
    - min_price : giá >=
    - max_price : giá <=
    """
    sql = "SELECT DISTINCT o.* FROM orders o"
    where: list[str] = []
    params: list = []

    if "book_id" in query:
        sql += " JOIN order_items i ON i.order_id = o.id"
        where.append("i.book_id = ?")
        params.append(query["book_id"])

    if "currency" in query:
        where.append("UPPER(o.currency) = UPPER(?)")
        params.append(query["currency"])

    if "min_price" in query:
        where.append("o.price >= ?")
        params.append(query["min_price"])

    if "max_price" in query:
        where.append("o.price <= ?")
        params.append(query["max_price"])

    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY o.id"

    with _db() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [_row_to_order(conn, r) for r in rows]


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()

    o1 = create_order({
        "items": [
            {"book_id": 1, "title": "Python 101",      "price": 10.0, "quantity": 2},
            {"book_id": 2, "title": "SQLite In Depth", "price": 15.5, "quantity": 1},
        ],
        "currency": "USD",
    })
    print("Created:", o1)

    o2 = create_order({
        "items": [{"book_id": 1, "title": "Python 101", "price": 10.0, "quantity": 1}],
        "price": 10.0,
        "currency": "VND",
    })
    print("Created:", o2)

    print("\nAll          :", get_all_orders())
    print("Find id=1    :", find_by_id(1))

    print("\nUpdate id=1  :", update_order(1, {"currency": "EUR"}))
    print("Query USD    :", get_order({"currency": "usd"}))
    print("Query book=1 :", get_order({"book_id": 1}))
    print("Query >=20   :", get_order({"min_price": 20}))

    print("\nDelete id=2  :", delete_order(2))
    print("Remaining    :", get_all_orders())