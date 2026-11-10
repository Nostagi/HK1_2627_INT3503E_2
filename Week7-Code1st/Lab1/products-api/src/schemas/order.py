
from marshmallow import Schema, fields, validate


class OrderItemInSchema(Schema):
    product_id = fields.Int(
        required=True,
        validate=validate.Range(min=1),
    )

    quantity = fields.Int(
        required=True,
        validate=validate.Range(min=1),
    )


class OrderInSchema(Schema):
    items = fields.List(
        fields.Nested(OrderItemInSchema),
        required=True,
        validate=validate.Length(min=1),
    )


class OrderListQuerySchema(Schema):
    page = fields.Int(
        load_default=1,
        validate=validate.Range(min=1),
    )

    per_page = fields.Int(
        load_default=10,
        validate=validate.Range(min=1, max=100),
    )

    sort = fields.Str(
        load_default="-created_at",
    )


class OrderItemOutSchema(Schema):
    id = fields.Int()

    order_id = fields.Int()

    product_id = fields.Int()

    quantity = fields.Int()

    unit_price_cents = fields.Int()


class OrderOutSchema(Schema):
    id = fields.Int()

    created_at = fields.DateTime()

    items = fields.List(
        fields.Nested(OrderItemOutSchema),
    )
