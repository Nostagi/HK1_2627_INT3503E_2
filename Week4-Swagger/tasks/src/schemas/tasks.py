from marshmallow import Schema, fields, validate, EXCLUDE


STATUS_VALUES   = ["todo", "in_progress", "done", "cancelled"]
PRIORITY_VALUES = ["low", "medium", "high", "urgent"]


class TaskSchema(Schema):
    """Task đầy đủ — dùng cho response."""
    id         = fields.Int(dump_only=True)
    title      = fields.Str(required=True)
    status     = fields.Str(required=True)
    priority   = fields.Str(required=True)
    dueDate    = fields.Date(required=True)     # render date picker trên Swagger UI
    assignedID = fields.Int(required=True)


class TaskInputSchema(Schema):
    """Payload tạo task mới — POST /tasks."""
    class Meta:
        unknown = EXCLUDE

    title      = fields.Str(required=True, validate=validate.Length(min=1))
    status     = fields.Str(required=True, validate=validate.OneOf(STATUS_VALUES))
    priority   = fields.Str(required=True, validate=validate.OneOf(PRIORITY_VALUES))
    dueDate    = fields.Date(required=True)
    assignedID = fields.Int(required=True)


class TaskUpdateSchema(Schema):
    """Payload cập nhật một phần — PATCH /tasks/{id}. Tất cả field optional."""
    class Meta:
        unknown = EXCLUDE

    title      = fields.Str(validate=validate.Length(min=1))
    status     = fields.Str(validate=validate.OneOf(STATUS_VALUES))
    priority   = fields.Str(validate=validate.OneOf(PRIORITY_VALUES))
    dueDate    = fields.Date()
    assignedID = fields.Int()


class TaskListSchema(Schema):
    """Response của GET /tasks."""
    data        = fields.List(fields.Nested(TaskSchema))
    next_cursor = fields.Str(allow_none=True)
    has_more    = fields.Bool()