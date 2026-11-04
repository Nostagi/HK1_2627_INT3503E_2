from flask import Flask

from src.handlers.config import DefaultConfig
from src.extensions import api, db, ma, migrate
from src.handlers.exception import register_error_handlers
from src.handlers.logging import configure_logging, register_request_logging


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

    # Đảm bảo Alembic thấy được model
    from src import models  # noqa: F401

    # Blueprints
    from src.views.health import health_bp
    from src.views.products import products_bp

    api.register_blueprint(products_bp)
    api.register_blueprint(health_bp)

    # Error handlers & request logging
    register_error_handlers(app)
    register_request_logging(app)

    return app

