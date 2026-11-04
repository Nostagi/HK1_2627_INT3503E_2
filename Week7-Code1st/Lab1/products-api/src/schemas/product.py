from marshmallow import Schema, ValidationError, fields, validate, validates_schema


class ProductOutSchema(Schema):
    id = fields.Int()
    sku = fields.Str()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    category = fields.Str()
    price_cents = fields.Int()
    qty_in_stock = fields.Int()
    status = fields.Str()
    archived = fields.Bool()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class ProductInSchema(Schema):
    sku = fields.Str(required=True, validate=validate.Regexp(r"^[A-Z0-9-]{3,64}$"))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(load_default=None, validate=validate.Length(max=1000))
    category = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    price_cents = fields.Int(required=True, validate=validate.Range(min=0))
    qty_in_stock = fields.Int(load_default=0, validate=validate.Range(min=0))


class ProductPatchSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True, validate=validate.Length(max=1000))
    category = fields.Str(validate=validate.Length(min=1, max=100))
    price_cents = fields.Int(validate=validate.Range(min=0))
    qty_in_stock = fields.Int(validate=validate.Range(min=0))
    archived = fields.Bool()

    @validates_schema
    def _at_least_one(self, data, **_):
        if not data:
            raise ValidationError("At least one field required")


class ProductListQuerySchema(Schema):
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))
    q = fields.Str(load_default=None)                                    # search name/sku
    category = fields.Str(load_default=None)
    status = fields.Str(
        load_default=None, validate=validate.OneOf(["in_stock", "out_of_stock", "archived"])
    )
    sort = fields.Str(load_default="-created_at")                        # -created_at | price_cents | name