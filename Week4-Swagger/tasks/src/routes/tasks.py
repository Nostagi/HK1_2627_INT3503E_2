from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint

from ..handlers.exception import ApiProblem

from ..schemas.tasks import (
    TaskInputSchema, 
    TaskSchema, TaskListSchema,
    TaskUpdateSchema
)
from ..schemas.exception import (ErrorSchema)

from ..services.tasks_service import (
    parse_pagination, PaginationArgs,
    decode_cursor, build_cursor_condition,
    list_tasks_service, get_task_service,
    create_task_service, update_task_service, delete_task_service,
)

blp = Blueprint(
    "tasks", __name__,
    url_prefix="/tasks",
    description="Operations on tasks",
)


# ----------------------------------------------------------------------
# /tasks
# ----------------------------------------------------------------------
@blp.route("/")
class TaskList(MethodView):

    @blp.response(200, TaskListSchema)
    @blp.alt_response(400, schema=ErrorSchema)
    @blp.alt_response(500, schema=ErrorSchema)
    def get(self):
        """List a page of tasks"""
        paginate: PaginationArgs = parse_pagination()

        cursor_value = request.args.get("cursor")
        if cursor_value:
            cursor = decode_cursor(cursor_value)
            if cursor["sort"] != paginate.sort_field:
                raise ApiProblem(
                    400, "Invalid cursor",
                    "Cursor does not match the requested sort.",
                    "cursor-sort-mismatch",
                )
            cursor_sql, cursor_params = build_cursor_condition(
                paginate.sort_field, paginate.descending, cursor,
            )
            paginate.filters.append(cursor_sql)
            paginate.params.extend(cursor_params)

        data, next_cursor, has_more = list_tasks_service(paginate)

        return {
            "data":        data,
            "next_cursor": next_cursor,
            "has_more":    has_more,
        }

    @blp.arguments(TaskInputSchema)
    @blp.response(201, TaskSchema)
    @blp.alt_response(400, schema=ErrorSchema)
    @blp.alt_response(500, schema=ErrorSchema)
    def post(self, payload):
        """Create a task"""
        return create_task_service(payload)


# ----------------------------------------------------------------------
# /tasks/{task_id}
# ----------------------------------------------------------------------
@blp.route("/<int:task_id>")
class TaskDetail(MethodView):

    @blp.response(200, TaskSchema)
    @blp.alt_response(404, schema=ErrorSchema)
    @blp.alt_response(500, schema=ErrorSchema)
    def get(self, task_id):
        """Get a specific task"""
        return get_task_service(task_id)

    @blp.arguments(TaskUpdateSchema)
    @blp.response(200, TaskSchema)
    @blp.alt_response(400, schema=ErrorSchema)
    @blp.alt_response(404, schema=ErrorSchema)
    @blp.alt_response(500, schema=ErrorSchema)
    def patch(self, payload, task_id):
        """Update a specific task"""
        return update_task_service(task_id, payload)

    @blp.response(204)
    @blp.alt_response(404, schema=ErrorSchema)
    @blp.alt_response(500, schema=ErrorSchema)
    def delete(self, task_id):
        """Delete a specific task"""
        delete_task_service(task_id)
        return "", 204