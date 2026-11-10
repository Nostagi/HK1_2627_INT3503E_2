from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload

from src.handlers.exception import Conflict, NotFound
from src.extensions import db
from src.models.product import Product
from src.schemas.product import (
    ProductInSchema,
    ProductListQuerySchema,
    ProductOutSchema,
    ProductPatchSchema,
)

products_bp = Blueprint(
    "products", 
    __name__, 
    url_prefix="/api/v1/products", 
    description="Products operations"
)


def _sorted(stmt, sort: str):
    direction = "-" if sort.startswith("-") else "+"
    col_name = sort.lstrip("+-")
    col = getattr(Product, col_name, Product.created_at)
    return stmt.order_by(col.desc() if direction == "-" else col.asc())


@products_bp.route("/")
class ProductListResource(MethodView):
    @products_bp.arguments(ProductListQuerySchema, location="query")
    @products_bp.response(200, ProductOutSchema(many=True))
    def get(self, args):
        """GET danh sách sản phẩm – trả về ARRAY + pagination qua headers."""
        stmt = db.select(Product)

        # filters
        if args.get("q"):
            like = f"%{args['q']}%"
            stmt = stmt.where(or_(Product.name.ilike(like), Product.sku.ilike(like)))
        if args.get("category"):
            stmt = stmt.where(Product.category == args["category"])
        if args.get("status") == "archived":
            stmt = stmt.where(Product.archived.is_(True))
        elif args.get("status") == "in_stock":
            stmt = stmt.where(Product.archived.is_(False), Product.qty_in_stock > 0)
        elif args.get("status") == "out_of_stock":
            stmt = stmt.where(Product.archived.is_(False), Product.qty_in_stock == 0)

        # total count (trước paginate)
        total = db.session.scalar(
            db.select(func.count()).select_from(stmt.subquery())
        ) or 0

        page = args["page"]
        per_page = args["per_page"]

        stmt = _sorted(stmt, args["sort"]).limit(per_page).offset((page - 1) * per_page)
        items = list(db.session.scalars(stmt).all())

        total_pages = (total + per_page - 1) // per_page if per_page else 0
        headers = {
            "X-Total-Count": str(total),
            "X-Page": str(page),
            "X-Per-Page": str(per_page),
            "X-Total-Pages": str(total_pages),
        }
        return items, 200, headers

    @products_bp.arguments(ProductInSchema)
    @products_bp.response(201, ProductOutSchema)
    def post(self, data):
        """POST tạo sản phẩm mới`."""

        if db.session.scalar(db.select(Product).where(Product.sku == data["sku"])):
            raise Conflict(f"SKU '{data['sku']}' already exists")
        product = Product(**data)
        db.session.add(product)
        db.session.commit()
        return product


@products_bp.route("/<int:product_id>")
class ProductResource(MethodView):
    @products_bp.response(200, ProductOutSchema)
    def get(self, product_id: int):
        """GET chi tiết sản phẩm."""

        p = db.session.get(Product, product_id)
        if not p:
            raise NotFound(f"Product {product_id} not found")
        return p

    @products_bp.arguments(ProductPatchSchema)
    @products_bp.response(200, ProductOutSchema)
    def patch(self, data, product_id: int):
        """PATCH cập nhật thông tin sản phẩm."""

        p = db.session.get(Product, product_id)
        if not p:
            raise NotFound(f"Product {product_id} not found")
        for k, v in data.items():
            setattr(p, k, v)
        db.session.commit()
        return p

    @products_bp.response(204)
    def delete(self, product_id: int):
        """DELETE xóa sản phẩm."""

        p = db.session.get(Product, product_id)
        if not p:
            raise NotFound(f"Product {product_id} not found")
        db.session.delete(p)
        db.session.commit()
        return ""