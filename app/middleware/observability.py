from __future__ import annotations

import json
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.config import get_settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
        }
        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id
        return json.dumps(payload, ensure_ascii=False)



def configure_logging() -> None:
    settings = get_settings()
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(level=logging.INFO)
    if settings.json_logs:
        for handler in root.handlers:
            handler.setFormatter(JsonFormatter())
    root.setLevel(logging.INFO)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        request_id = request.headers.get(settings.request_id_header_name) or str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers[settings.request_id_header_name] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        logging.getLogger("app.request").info(
            "%s %s -> %s in %sms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            extra={"request_id": request_id},
        )
        return response


@dataclass
class _Bucket:
    events: Deque[float]


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._buckets: dict[str, _Bucket] = defaultdict(lambda: _Bucket(deque()))

    def _limit_for_path(self, path: str) -> int | None:
        settings = get_settings()
        if path.startswith("/api/auth/"):
            return settings.rate_limit_auth_per_minute
        if path.startswith("/api/reports/upload"):
            return settings.rate_limit_upload_per_minute
        if path.startswith("/api/vapi/"):
            return settings.rate_limit_vapi_per_minute
        return None

    async def dispatch(self, request: Request, call_next):
        limit = self._limit_for_path(request.url.path)
        if not limit:
            return await call_next(request)

        ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (request.client.host if request.client else "unknown")
        key = f"{request.url.path}:{ip}"
        now = time.monotonic()
        window_start = now - 60
        bucket = self._buckets[key].events
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= limit:
            request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please retry shortly."},
                headers={get_settings().request_id_header_name: request_id, "Retry-After": "60"},
            )
        bucket.append(now)
        return await call_next(request)
