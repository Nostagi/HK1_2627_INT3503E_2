
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


class OrderItemPatchSchema(Schema):
    quantity = fields.Int(
        required=True,
        validate=validate.Range(min=1),
    )


class OrderItemOutSchema(Schema):
    id = fields.Int()

    order_id = fields.Int()

    product_id = fields.Int()

    quantity = fields.Int()

    unit_price_cents = fields.Int()
