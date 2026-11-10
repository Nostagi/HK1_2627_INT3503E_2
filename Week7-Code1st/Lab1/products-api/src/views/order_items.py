
from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy.orm import selectinload

from src.handlers.exception import Conflict, NotFound
from src.extensions import db

from src.models.order import Order, OrderItem
from src.models.product import Product
from src.schemas.order_item import (
    OrderItemInSchema,
    OrderItemPatchSchema,
    OrderItemOutSchema,
)


order_items_bp = Blueprint(
    "order_items",
    __name__,
    url_prefix="/api/v1/orders",
    description="Order items operations",
)


@order_items_bp.route("/<int:order_id>/items")
class OrderItemListResource(MethodView):

    @order_items_bp.response(200, OrderItemOutSchema(many=True), )
    def get(self, order_id: int):
        """GET danh sách OrderItem."""

        order = db.session.get(
            Order,
            order_id,
        )

        if not order:
            raise NotFound(
                f"Order {order_id} not found"
            )

        stmt = (
            db.select(OrderItem)
            .where(OrderItem.order_id == order_id)
            .options(
                selectinload(OrderItem.product)
            )
        )

        items = list(
            db.session.scalars(stmt).all()
        )

        return items

    @order_items_bp.arguments(OrderItemInSchema, )
    @order_items_bp.response(201, OrderItemOutSchema, )
    def post(self, data, order_id: int):
        """POST thêm OrderItem vào Order."""

        order = db.session.get(
            Order,
            order_id,
        )

        if not order:
            raise NotFound(
                f"Order {order_id} not found"
            )

        product = db.session.get(
            Product,
            data["product_id"],
        )

        if not product:
            raise NotFound(
                f"Product {data['product_id']} not found"
            )

        if product.archived:
            raise Conflict(
                f"Product {product.id} is archived"
            )

        item = OrderItem(
            order=order,
            product=product,
            quantity=data["quantity"],
            unit_price_cents=product.price_cents,
        )

        db.session.add(item)

        db.session.commit()

        return item


@order_items_bp.route("/items/<int:item_id>")
class OrderItemResource(MethodView):

    @order_items_bp.response(200, OrderItemOutSchema, )
    def get(self, item_id: int):
        """GET chi tiết OrderItem."""

        item = db.session.get(
            OrderItem,
            item_id,
        )

        if not item:
            raise NotFound(
                f"OrderItem {item_id} not found"
            )

        return item

    @order_items_bp.arguments(OrderItemPatchSchema, )
    @order_items_bp.response(200, OrderItemOutSchema, )
    def patch(self, data, item_id: int):
        """PATCH cập nhật OrderItem."""

        item = db.session.get(
            OrderItem,
            item_id,
        )

        if not item:
            raise NotFound(
                f"OrderItem {item_id} not found"
            )

        item.quantity = data["quantity"]

        db.session.commit()

        return item

    @order_items_bp.response(204, )
    def delete(self, item_id: int):
        """DELETE OrderItem."""

        item = db.session.get(
            OrderItem,
            item_id,
        )

        if not item:
            raise NotFound(
                f"OrderItem {item_id} not found"
            )

        db.session.delete(item)

        db.session.commit()

        return ""
