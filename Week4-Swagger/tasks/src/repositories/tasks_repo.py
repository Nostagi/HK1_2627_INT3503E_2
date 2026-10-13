from ..database.tasks_db import get_db

COLUMNS = ("id", "title", "status", "priority", "dueDate", "assignedID")
_COLUMN_LIST = ", ".join(COLUMNS)


def query_tasks(paginate):
    """Trả về tối đa `limit + 1` row để biết còn trang sau hay không."""
    where_sql = ""
    if paginate.filters:
        where_sql = "WHERE " + " AND ".join(paginate.filters)

    direction = "DESC" if paginate.descending else "ASC"

    sql = f"""
        SELECT {_COLUMN_LIST}
        FROM tasks
        {where_sql}
        ORDER BY {paginate.sort_field} {direction}, id {direction}
        LIMIT ?
    """

    conn = get_db()
    try:
        return conn.execute(sql, paginate.params + [paginate.limit + 1]).fetchall()
    finally:
        conn.close()


def get_task_by_id(task_id: int):
    conn = get_db()
    try:
        return conn.execute(
            f"SELECT {_COLUMN_LIST} FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
    finally:
        conn.close()


def insert_task(data: dict) -> int:
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO tasks (title, status, priority, dueDate, assignedID) "
            "VALUES (?, ?, ?, ?, ?)",
            (data["title"], data["status"], data["priority"],
             data["dueDate"], data["assignedID"]),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_task(task_id: int, updates: dict) -> int:
    if not updates:
        return 0
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    params = list(updates.values()) + [task_id]

    conn = get_db()
    try:
        cur = conn.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", params)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def delete_task(task_id: int) -> int:
    conn = get_db()
    try:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()