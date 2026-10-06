import base64
from typing import Any
from dataclasses import dataclass
import json

from flask import Flask, jsonify, request

from exception import ApiProblem as ProblemError
from orders_db import get_db

app = Flask(__name__)

LOCALHOST:dict = {
    "host" : "127.0.0.1",
    "port" : 5000,
    "debug" : True      # only for localhost3
}

ALLOWED_FILTERS = {"status", "customer_id"}
ALLOWED_SORT_FIELDS = {"id", "customer_id", "status"}
ALLOWED_FIELDS = {"id", "customer_id", "status", "cart"}


#----------------------
# Cursor Pagination utils
#----------------------
@dataclass
class PaginationArgs:
    limit: int                  # maximum number of records to return
    fields: list[str]           # which fields to include in the response
    sort_field: str             # which field to sort by (must be in ALLOWED_SORT_FIELDS)
    descending: bool            # True if sort is descending, False if ascending
    filters: list[str]          # SQL WHERE conditions for filtering
    params: list[Any]


def parse_pagination():

    def parse_sort():
        """
        Supported:
            sort=id
            sort=-id
            sort=customer_id
            sort=-customer_id
            sort=status
            sort=-status

        A unique secondary key (id) is always used to make pagination stable.
        """
        value = request.args.get("sort", "id")

        descending = value.startswith("-")
        field = value[1:] if descending else value

        if field not in ALLOWED_SORT_FIELDS:
            raise ProblemError(
                status=400,
                title="Invalid sort",
                detail=f"Unsupported sort field: {field}",
                type_path="invalid-sort",
            )

        return field, descending


    def parse_limit():
        raw = request.args.get("limit", "10")

        try:
            limit = int(raw)
        except ValueError:
            raise ProblemError(
                status=400,
                title="Invalid limit",
                detail="limit must be an integer.",
                type_path="invalid-limit",
            )

        if limit < 1 or limit > 100:
            raise ProblemError(
                status=400,
                title="Invalid limit",
                detail="limit must be between 1 and 100.",
                type_path="invalid-limit",
            )

        return limit


    def parse_fields():
        raw = request.args.get("fields")

        if not raw:
            return ["id", "customer_id", "status", "cart"]

        fields = [item.strip() for item in raw.split(",") if item.strip()]

        invalid = [field for field in fields if field not in ALLOWED_FIELDS]
        if invalid:
            raise ProblemError(
                status=400,
                title="Invalid fields",
                detail=f"Unsupported fields: {', '.join(invalid)}",
                type_path="invalid-fields",
            )

        if not fields:
            raise ProblemError(
                status=400,
                title="Invalid fields",
                detail="fields must contain at least one valid field.",
                type_path="invalid-fields",
            )

        return fields


    def parse_filters():
        filters = []
        params = []

        status = request.args.get("status")
        if status is not None:
            filters.append("status = ?")
            params.append(status)

        customer_id = request.args.get("customer_id")
        if customer_id is not None:
            try:
                customer_id = int(customer_id)
            except ValueError:
                raise ProblemError(
                    status=400,
                    title="Invalid customer_id",
                    detail="customer_id must be an integer.",
                    type_path="invalid-customer-id",
                )

            filters.append("customer_id = ?")
            params.append(customer_id)

        return filters, params

    limit = parse_limit()
    fields = parse_fields()
    sort_field, descending = parse_sort()
    filters, params = parse_filters()

    return PaginationArgs(
        limit=limit,
        fields=fields,
        sort_field=sort_field,
        descending=descending,
        filters=filters,
        params=params,
    )
    
    
def encode_cursor(sort_field, sort_value, order_id):
    payload = {
        "sort": sort_field,
        "value": sort_value,
        "id": order_id,
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_cursor(cursor):
    try:
        padding = "=" * (-len(cursor) % 4)
        raw = base64.urlsafe_b64decode((cursor + padding).encode("ascii"))
        payload = json.loads(raw.decode("utf-8"))

        if (
            not isinstance(payload, dict)
            or payload.get("sort") not in ALLOWED_SORT_FIELDS
            or "value" not in payload
            or not isinstance(payload.get("id"), int)
        ):
            raise ValueError

        return payload
    except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
        raise ProblemError(
            status=400,
            title="Invalid cursor",
            detail="The cursor is malformed or invalid.",
            type_path="invalid-cursor",
        )


def build_cursor_condition(sort_field, descending, cursor):
    """
    Keyset condition using (sort_field, id) as the cursor key.

    ASC:
        field > cursor.value
        OR (field = cursor.value AND id > cursor.id)

    DESC:
        field < cursor.value
        OR (field = cursor.value AND id < cursor.id)
    """
    operator = "<" if descending else ">"

    sql = (
        f"({sort_field} {operator} ? "
        f"OR ({sort_field} = ? AND id {operator} ?))"
    )

    value = cursor["value"]
    order_id = cursor["id"]

    return sql, [value, value, order_id]


def row_to_dict(row, fields):
    result = {}

    for field in fields:
        value = row[field]

        if field == "cart":
            value = json.loads(value)

        result[field] = value

    return result


#----------------------
# Route
#----------------------

@app.get("/orders")
def get_orders():
    paginate = parse_pagination()

    with request.args.get("cursor") as cursor_value:  
        if cursor_value:
            cursor = decode_cursor(cursor_value)
            if cursor["sort"] != paginate.sort_field:
                raise ProblemError(
                    status=400,
                    title="Invalid cursor",
                    detail="Cursor does not match the requested sort.",
                    type_path="cursor-sort-mismatch",
                )
            cursor_sql, cursor_params = build_cursor_condition(
                paginate.sort_field,
                paginate.descending,
                cursor,
            )
            paginate.filters.append(cursor_sql)
            paginate.params.extend(cursor_params)

    data, next_cursor, has_more = get_orders_service(paginate)

    return jsonify(
        {
            "data": data,
            "next_cursor": next_cursor,
            "has_more": has_more,
        }
    )

#----------------------
# Services
#----------------------

def get_orders_service(paginate: PaginationArgs):
    rows = query_orders(paginate)       # Query next page with an extra row as marker
        
    has_more = len(rows) > paginate.limit
    
    data = [row_to_dict(row, paginate.fields) for row in rows[:paginate.limit]]
    next_cursor = None
    
    if has_more and rows:
        next_page_first_row = rows[paginate.limit]
        next_cursor = encode_cursor(
            paginate.sort_field,
            next_page_first_row[paginate.sort_field],
            next_page_first_row["id"],
        )

    return data, next_cursor, has_more


#----------------------
# Repository
#----------------------

def query_orders(paginate: PaginationArgs):
    where_sql = ""
    if paginate.filters:
        where_sql = "WHERE " + " AND ".join(paginate.filters)

    direction = "DESC" if paginate.descending else "ASC"
        
    # Fetch one extra record to determine whether another page exists.
    sql = f"""
        SELECT id, customer_id, status, cart
        FROM orders
        {where_sql}
        ORDER BY {paginate.sort_field} {direction}, id {direction}
        LIMIT ?
    """
    paginate.params.append(paginate.limit + 1)

    conn = get_db()
    try:
        rows = conn.execute(sql, paginate.params).fetchall()
    finally:
        conn.close()
        return rows


#----------------------
# Application
#----------------------

if __name__ == "__main__":
    from orders_db import init_db
    init_db(seed=True)

    app.run(**LOCALHOST)
