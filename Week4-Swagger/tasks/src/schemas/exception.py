from marshmallow import Schema, fields, INCLUDE

class ErrorSchema(Schema):
    """RFC 7807 — Problem Details for HTTP APIs."""
    class Meta:
        unknown = INCLUDE

    type      = fields.Str()
    status    = fields.Int()
    title     = fields.Str()
    detail    = fields.Str()
    instance  = fields.Str()
    trace_id  = fields.Str()