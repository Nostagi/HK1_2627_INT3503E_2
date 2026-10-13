from flask import Flask
from flask_smorest import Api

from src.routes.tasks import blp as TasksBlueprint
from src.schemas.exception import ErrorSchema
from src.handlers.exception import register_error_handlers


LOCALHOST = {
    "host": "127.0.0.1",
    "port": 5000,
    "debug": True,   # chỉ dùng cho localhost
}

app = Flask(__name__)

# Cấu hình OpenAPI
app.config.update(
    API_TITLE="Internal Task Management API",
    API_VERSION="v1",
    OPENAPI_VERSION="3.0.3",
    OPENAPI_URL_PREFIX="/",
    OPENAPI_JSON_PATH="openapi.json",      # -> /openapi.json
    OPENAPI_SWAGGER_UI_PATH="/docs",        # -> /docs
    OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
)

# ----------------------------------------------------------------------
# Api instance
# ----------------------------------------------------------------------
# Ghi đè schema lỗi mặc định của flask-smorest bằng ErrorSchema (RFC 7807)
# api.ERROR_SCHEMA = ErrorSchema
api = Api(app)

# Đăng ký các blueprints
api.register_blueprint(TasksBlueprint)

# Đăng ký các error handler của ApiProblem / HTTPException / fallback
register_error_handlers(app)


# ----------------------------------------------------------------------
# Entrypoint
# ----------------------------------------------------------------------

if __name__ == "__main__":
    from src.database.tasks_db import init_db
    init_db()
    app.run(**LOCALHOST)