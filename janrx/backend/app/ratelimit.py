import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Request

from .errors import ApiError


class SlidingWindowLimiter:
    """In-memory limiter. Per-process only: use Redis if running several instances."""

    def __init__(self, limit: int, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> tuple[bool, int]:
        now = time.monotonic()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] >= self.window:
                q.popleft()
            if len(q) >= self.limit:
                return False, max(1, int(self.window - (now - q[0])) + 1)
            q.append(now)
            return True, 0


def client_key(request: Request) -> str:
    if request.app.state.settings.trust_proxy:
        fwd = request.headers.get("x-forwarded-for")
        if fwd:
            return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def ocr_rate_limit(request: Request) -> None:
    allowed, retry = request.app.state.limiter.check(client_key(request))
    if not allowed:
        request.app.state.metrics.inc("ocr rate_limited")
        raise ApiError(429, "RATE_LIMITED", "Too many scan requests. Please wait a moment, or type the names instead.",
                       fallback="manual_entry", headers={"Retry-After": str(retry)})
