from flask import jsonify
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str = "Internal error", *, status_code: int | None = None,
                 code: str | None = None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code


class NotFound(ApiError):
    status_code = 404
    code = "not_found"


class Conflict(ApiError):
    status_code = 409
    code = "conflict"


class OutOfStock(ApiError):
    status_code = 409
    code = "out_of_stock"


class BadRequest(ApiError):
    status_code = 400
    code = "bad_request"


class ValidationFailed(ApiError):
    status_code = 422
    code = "validation_failed"


def _envelope(code: str, message: str):
    return jsonify({"error": {"code": code, "message": message}})


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def _api_err(e: ApiError):
        return _envelope(e.code, e.message), e.status_code

    @app.errorhandler(HTTPException)
    def _http_err(e: HTTPException):
        code = (e.name or "http_error").lower().replace(" ", "_")
        return _envelope(code, e.description or ""), e.code

    @app.errorhandler(Exception)
    def _uncaught(e: Exception):
        app.logger.exception("Unhandled exception")
        return _envelope("internal_error", "Internal server error"), 500