from flask import Flask

from src.handlers.config import DefaultConfig
from src.extensions import api, db, ma, migrate
from src.handlers.exception import register_error_handlers
from src.handlers.logging import configure_logging, register_request_logging

# Đảm bảo Alembic thấy được model
from src import models  # noqa: F401

# Blueprints
from src.views.health import health_bp
from src.views.products import products_bp
from src.views.orders import orders_bp


def create_app(config_class=DefaultConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Logging sớm để bắt được cả lỗi khởi tạo
    configure_logging(app)

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    api.init_app(app)

    # Blueprints
    api.register_blueprint(products_bp)
    api.register_blueprint(health_bp)
    api.register_blueprint(orders_bp)

    # Error handlers & request logging
    register_error_handlers(app)
    register_request_logging(app)

    return app


if __name__ == "__main__":
    from .seed import seed
    app = seed()

    LOCALHOST = {
        "host": "0.0.0.9",
        "port": 5000,
        "debug": True,
    }

    app.run(**LOCALHOST)

