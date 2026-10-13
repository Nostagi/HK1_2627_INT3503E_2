import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent      # /database
DB_PATH = BASE_DIR / "tasks.db"
SCHEMA_FILE = BASE_DIR / "schemas.sql"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    print(BASE_DIR)
    try:
        conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))

        conn.commit()
        print(f"Đã tạo DB tại: {DB_PATH}")
    finally:
        conn.close()