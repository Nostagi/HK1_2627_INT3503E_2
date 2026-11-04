import json
import logging
import sys
import time
import uuid

from flask import g, request


class JsonFormatter(logging.Formatter):
    """Structured JSON log: ts, level, msg, rid, status, ms."""
    _extra = ("rid", "status", "ms", "method", "path")

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "msg": record.getMessage(),
        }
        for f in self._extra:
            if hasattr(record, f):
                payload[f] = getattr(record, f)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(app):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(app.config.get("LOG_LEVEL", "INFO"))


def register_request_logging(app):
    @app.before_request
    def _start():
        g._t0 = time.perf_counter()
        g.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    @app.after_request
    def _end(response):
        ms = round((time.perf_counter() - g._t0) * 1000, 2)
        response.headers["X-Request-ID"] = g.request_id
        app.logger.info(
            "request",
            extra={
                "rid": g.request_id,
                "status": response.status_code,
                "ms": ms,
                "method": request.method,
                "path": request.path,
            },
        )
        return response