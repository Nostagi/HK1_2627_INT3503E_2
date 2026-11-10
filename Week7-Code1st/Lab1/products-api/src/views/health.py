from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy import text

from ..extensions import db

health_bp = Blueprint("health", __name__, url_prefix="/")


@health_bp.route("/healthz")
class Liveness(MethodView):
    def get(self):
        """GET kiểm tra trạng thái liveness (KHÔNG phụ thuộc DB) của process."""
        # Liveness: chỉ cần process sống, KHÔNG phụ thuộc DB

        return {"status": "ok"}


@health_bp.route("/ready")
class Readiness(MethodView):
    def get(self):
        """GET kiểm tra trạng thái readiness (phụ thuộc DB) của process."""
        # Readiness: process có thể nhận request hay không, phụ thuộc DB

        try:
            db.session.execute(text("SELECT 1"))
            return {"status": "ready", "db": "ok"}
        except Exception:
            return {"status": "not_ready", "db": "error"}, 503