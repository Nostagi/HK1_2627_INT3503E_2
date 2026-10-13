from __future__ import annotations

import logging
import uuid

from flask import jsonify, request
from werkzeug.exceptions import HTTPException


ERROR_BASE = "/errors"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# ApiProblem
# ----------------------------------------------------------------------
class ApiProblem(Exception):
    def __init__(self, status, title, detail=None, type_path=None, **extra):
        self.type     = f"{ERROR_BASE}/{type_path}" if type_path else "about:blank"
        self.status   = status
        self.title    = title
        self.detail   = detail
        self.trace_id = str(uuid.uuid4())
        self.extra    = extra

    def _to_response(self):
        body = {
            "type":     self.type,
            "status":   self.status,
            "title":    self.title,
            "instance": request.path,
            "trace_id": self.trace_id,
        }
        if self.detail:
            body["detail"] = self.detail
        body.update(self.extra)

        resp = jsonify(body)
        resp.status_code = self.status
        resp.headers["Content-Type"] = "application/problem+json"
        return resp

    @staticmethod
    def from_http_exception(error: HTTPException) -> "ApiProblem":
        return ApiProblem(
            status    = error.code or 500,
            title     = error.name,
            detail    = error.description,
            type_path = f"http-{error.code}",
        )


# ----------------------------------------------------------------------
# Đăng ký error handlers
# ----------------------------------------------------------------------
def register_error_handlers(app):

    @app.errorhandler(ApiProblem)
    def handle_api_problem(error: ApiProblem):
        return error._to_response()

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        return ApiProblem.from_http_exception(error)._to_response()

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        problem = ApiProblem(
            status    = 500,
            title     = "Internal Server Error",
            detail    = "An unexpected error occurred.",
            type_path = "internal-server-error",
        )
        logger.exception(
            "Unhandled exception | trace_id=%s | error_type=%s | "
            "error=%s | endpoint=%s | query=%s | request-body=%s",
            problem.trace_id,
            type(error).__name__,
            str(error),
            f"{request.method} {request.path}",
            request.args.to_dict(),
            request.get_json(silent=True),
        )
        return problem._to_response()