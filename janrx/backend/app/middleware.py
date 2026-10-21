import logging
import re
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware

from .context import request_id_var

log = logging.getLogger("janrx")
_VALID_ID = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assigns a request ID, logs one structured line per request, counts metrics."""

    async def dispatch(self, request, call_next):
        incoming = request.headers.get("x-request-id", "")
        rid = incoming if _VALID_ID.match(incoming) else uuid.uuid4().hex
        token = request_id_var.set(rid)
        start = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            route = request.scope.get("route")
            path = getattr(route, "path", "unmatched")
            ms = round((time.perf_counter() - start) * 1000, 1)
            request.app.state.metrics.inc(f"http {request.method} {path} {status}")
            log.info("request", extra={"fields": {
                "method": request.method, "path": path, "status": status, "duration_ms": ms}})
            request_id_var.reset(token)
