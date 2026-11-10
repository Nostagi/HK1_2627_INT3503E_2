from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload

from src.handlers.exception import Conflict, NotFound
from src.extensions import db

from src.models.order import Order, OrderItem
from src.models.product import Product
from src.schemas.order import (
    OrderInSchema,
    OrderListQuerySchema,
    OrderOutSchema,
)

orders_bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/api/v1/orders",
    description="Orders operations",
)


def _sorted(stmt, sort: str):
    direction = "-" if sort.startswith("-") else "+"
    col_name = sort.lstrip("+-")

    col = getattr(Order, col_name, Order.created_at)

    return stmt.order_by(
        col.desc() if direction == "-" else col.asc()
    )


@orders_bp.route("/")
class OrderListResource(MethodView):

    @orders_bp.arguments(
        OrderListQuerySchema,
        location="query",
    )
    @orders_bp.response(200, OrderOutSchema(many=True), )
    def get(self, args):
        """GET danh sách Order."""

        stmt = db.select(Order)

        total = db.session.scalar(
            db.select(func.count()).select_from(
                stmt.subquery()
            )
        ) or 0

        page = args["page"]
        per_page = args["per_page"]

        stmt = (
            _sorted(stmt, args["sort"])
            .limit(per_page)
            .offset((page - 1) * per_page)
            .options(
                selectinload(Order.items)
            )
        )

        items = list(
            db.session.scalars(stmt).all()
        )

        total_pages = (
            (total + per_page - 1) // per_page
            if per_page
            else 0
        )

        headers = {
            "X-Total-Count": str(total),
            "X-Page": str(page),
            "X-Per-Page": str(per_page),
            "X-Total-Pages": str(total_pages),
        }

        return items, 200, headers

    @orders_bp.arguments(OrderInSchema)
    @orders_bp.response(201, OrderOutSchema, )
    def post(self, data):
        """POST tạo Order kèm OrderItem."""

        order = Order()

        db.session.add(order)

        for item_data in data["items"]:

            product = db.session.get(
                Product,
                item_data["product_id"],
            )

            if not product:
                raise NotFound(
                    f"Product {item_data['product_id']} not found"
                )

            if product.archived:
                raise Conflict(
                    f"Product {product.id} is archived"
                )

            item = OrderItem(
                product=product,
                quantity=item_data["quantity"],
                unit_price_cents=product.price_cents,
            )

            order.items.append(item)

        db.session.commit()

        return order


@orders_bp.route("/<int:order_id>")
class OrderResource(MethodView):

    @orders_bp.response(200, OrderOutSchema, )
    def get(self, order_id: int):
        """GET chi tiết Order."""

        stmt = (
            db.select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items)
            )
        )

        order = db.session.scalar(stmt)

        if not order:
            raise NotFound(
                f"Order {order_id} not found"
            )

        return order

    @orders_bp.response(204, )
    def delete(self, order_id: int):
        """DELETE Order."""

        order = db.session.get(
            Order,
            order_id,
        )

        if not order:
            raise NotFound(
                f"Order {order_id} not found"
            )

        db.session.delete(order)

        db.session.commit()

        return ""
