import base64
import json
from dataclasses import dataclass, field
from datetime import date

from flask import request

from ..handlers.exception import ApiProblem
from ..repositories import tasks_repo


ALLOWED_SORT_FIELDS = {"id", "title", "status", "priority", "dueDate", "assignedID"}
ALLOWED_FIELDS      = {"id", "title", "status", "priority", "dueDate", "assignedID"}
ALLOWED_STATUS      = {"todo", "in_progress", "done", "cancelled"}
ALLOWED_PRIORITY    = {"low", "medium", "high", "urgent"}
DEFAULT_FIELDS      = ["id", "title", "status", "priority", "dueDate", "assignedID"]


@dataclass
class PaginationArgs:
    limit: int
    fields: list
    sort_field: str
    descending: bool
    filters: list = field(default_factory=list)
    params: list = field(default_factory=list)


# ----------------------------------------------------------------------
# Parse query params
# ----------------------------------------------------------------------

def _parse_limit() -> int:
    raw = request.args.get("limit", "10")
    try:
        limit = int(raw)
    except (TypeError, ValueError):
        raise ApiProblem(400, "Invalid limit", "limit must be an integer.", "invalid-limit")
    if not 1 <= limit <= 100:
        raise ApiProblem(400, "Invalid limit", "limit must be between 1 and 100.", "invalid-limit")
    return limit


def _parse_fields() -> list:
    raw = request.args.get("fields")
    if not raw:
        return list(DEFAULT_FIELDS)

    fields = [f.strip() for f in raw.split(",") if f.strip()]
    if not fields:
        raise ApiProblem(400, "Invalid fields",
                         "fields must contain at least one valid field.", "invalid-fields")

    invalid = [f for f in fields if f not in ALLOWED_FIELDS]
    if invalid:
        raise ApiProblem(400, "Invalid fields",
                         f"Unsupported fields: {', '.join(invalid)}", "invalid-fields")
    return fields


def _parse_sort() -> tuple[str, bool]:
    value = request.args.get("sort", "id")
    descending = value.startswith("-")
    field = value[1:] if descending else value
    if field not in ALLOWED_SORT_FIELDS:
        raise ApiProblem(400, "Invalid sort",
                         f"Unsupported sort field: {field}", "invalid-sort")
    return field, descending


def _parse_filters() -> tuple[list, list]:
    filters: list = []
    params: list = []

    status = request.args.get("status")
    if status is not None:
        if status not in ALLOWED_STATUS:
            raise ApiProblem(400, "Invalid status",
                             f"status must be one of: {', '.join(sorted(ALLOWED_STATUS))}",
                             "invalid-status")
        filters.append("status = ?")
        params.append(status)

    priority = request.args.get("priority")
    if priority is not None:
        if priority not in ALLOWED_PRIORITY:
            raise ApiProblem(400, "Invalid priority",
                             f"priority must be one of: {', '.join(sorted(ALLOWED_PRIORITY))}",
                             "invalid-priority")
        filters.append("priority = ?")
        params.append(priority)

    assigned_raw = request.args.get("assignedID")
    if assigned_raw is not None:
        try:
            assigned_id = int(assigned_raw)
        except (TypeError, ValueError):
            raise ApiProblem(400, "Invalid assignedID",
                             "assignedID must be an integer.", "invalid-assigned-id")
        filters.append("assignedID = ?")
        params.append(assigned_id)

    return filters, params


def parse_pagination() -> PaginationArgs:
    limit = _parse_limit()
    fields = _parse_fields()
    sort_field, descending = _parse_sort()
    filters, params = _parse_filters()

    return PaginationArgs(
        limit=limit,
        fields=fields,
        sort_field=sort_field,
        descending=descending,
        filters=filters,
        params=params,
    )


# ----------------------------------------------------------------------
# Cursor utils (Linked-list style pagination)
# ----------------------------------------------------------------------

def encode_cursor(sort_field, sort_value, task_id) -> str:
    payload = {"sort": sort_field, "value": sort_value, "id": task_id}
    raw = json.dumps(payload, separators=(",", ":"), default=str).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_cursor(cursor: str) -> dict:
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
        raise ApiProblem(400, "Invalid cursor",
                         "The cursor is malformed or invalid.", "invalid-cursor")


def build_cursor_condition(sort_field: str, descending: bool, cursor: dict):
    """
    Keyset condition dùng (sort_field, id) làm khóa con trỏ.

    ASC : field > v OR (field = v AND id > cursor.id)
    DESC: field < v OR (field = v AND id < cursor.id)
    """
    operator = "<" if descending else ">"
    sql = f"({sort_field} {operator} ? OR ({sort_field} = ? AND id {operator} ?))"
    return sql, [cursor["value"], cursor["value"], cursor["id"]]


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def row_to_dict(row, fields) -> dict:
    result = {field: row[field] for field in fields}
    # SQLite lưu dueDate dạng TEXT -> convert về date để Marshmallow serialize đúng
    if "dueDate" in result and isinstance(result["dueDate"], str):
        result["dueDate"] = date.fromisoformat(result["dueDate"])
    return result


def _validate_task_payload(payload: dict, partial: bool) -> dict:
    if not isinstance(payload, dict):
        raise ApiProblem(400, "Invalid body",
                         "Request body must be a JSON object.", "invalid-body")

    required = {"title", "status", "priority", "dueDate", "assignedID"}
    allowed = required

    unknown = set(payload) - allowed
    if unknown:
        raise ApiProblem(400, "Unknown fields",
                         f"Unknown fields: {', '.join(sorted(unknown))}",
                         "unknown-fields")

    if not partial:
        missing = required - set(payload)
        if missing:
            raise ApiProblem(400, "Missing fields",
                             f"Missing required fields: {', '.join(sorted(missing))}",
                             "missing-fields")

    result: dict = {}

    if "title" in payload:
        v = payload["title"]
        if not isinstance(v, str) or not v.strip():
            raise ApiProblem(400, "Invalid title",
                             "title must be a non-empty string.", "invalid-title")
        result["title"] = v.strip()

    if "status" in payload:
        v = payload["status"]
        if v not in ALLOWED_STATUS:
            raise ApiProblem(400, "Invalid status",
                             f"status must be one of: {', '.join(sorted(ALLOWED_STATUS))}",
                             "invalid-status")
        result["status"] = v

    if "priority" in payload:
        v = payload["priority"]
        if v not in ALLOWED_PRIORITY:
            raise ApiProblem(400, "Invalid priority",
                             f"priority must be one of: {', '.join(sorted(ALLOWED_PRIORITY))}",
                             "invalid-priority")
        result["priority"] = v

    if "dueDate" in payload:
        v = payload["dueDate"]
        if not isinstance(v, str):
            raise ApiProblem(400, "Invalid dueDate",
                             "dueDate must be a string in YYYY-MM-DD format.",
                             "invalid-due-date")
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ApiProblem(400, "Invalid dueDate",
                             "dueDate must be a valid date in YYYY-MM-DD format.",
                             "invalid-due-date")
        result["dueDate"] = v

    if "assignedID" in payload:
        v = payload["assignedID"]
        if isinstance(v, bool) or not isinstance(v, int):
            raise ApiProblem(400, "Invalid assignedID",
                             "assignedID must be an integer.", "invalid-assigned-id")
        result["assignedID"] = v

    return result


# ----------------------------------------------------------------------
# Business logic
# ----------------------------------------------------------------------

def list_tasks_service(paginate: PaginationArgs):
    rows = tasks_repo.query_tasks(paginate)

    has_more = len(rows) > paginate.limit
    page_rows = rows[: paginate.limit]
    data = [row_to_dict(r, paginate.fields) for r in page_rows]

    next_cursor = None
    if has_more and page_rows:
        # Cursor trỏ tới row CUỐI trang hiện tại,
        #    trang sau dùng `>` để lấy phần tử kế tiếp (linked-list style).
        last = page_rows[-1]
        next_cursor = encode_cursor(
            paginate.sort_field,
            last[paginate.sort_field],
            last["id"],
        )

    return data, next_cursor, has_more


def get_task_service(task_id: int) -> dict:
    row = tasks_repo.get_task_by_id(task_id)
    if row is None:
        raise ApiProblem(404, "Task not found",
                         f"Task with id {task_id} does not exist.",
                         "task-not-found", instance=f"/tasks/{task_id}")
    return row_to_dict(row, list(DEFAULT_FIELDS))


def create_task_service(payload: dict) -> dict:
    data = _validate_task_payload(payload, partial=False)
    new_id = tasks_repo.insert_task(data)
    return get_task_service(new_id)


def update_task_service(task_id: int, payload: dict) -> dict:
    if tasks_repo.get_task_by_id(task_id) is None:
        raise ApiProblem(404, "Task not found",
                         f"Task with id {task_id} does not exist.",
                         "task-not-found", instance=f"/tasks/{task_id}")

    data = _validate_task_payload(payload, partial=True)
    if not data:
        raise ApiProblem(400, "Empty update",
                         "PATCH body must contain at least one updatable field.",
                         "empty-update")

    tasks_repo.update_task(task_id, data)
    return get_task_service(task_id)


def delete_task_service(task_id: int) -> None:
    if tasks_repo.delete_task(task_id) == 0:
        raise ApiProblem(404, "Task not found",
                         f"Task with id {task_id} does not exist.",
                         "task-not-found", instance=f"/tasks/{task_id}")