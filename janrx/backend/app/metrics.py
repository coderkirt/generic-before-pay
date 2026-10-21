from collections import Counter
from threading import Lock


class Metrics:
    """In-memory counters for demo/debugging. No personal data."""

    def __init__(self) -> None:
        self._c: Counter[str] = Counter()
        self._lock = Lock()

    def inc(self, key: str) -> None:
        with self._lock:
            self._c[key] += 1

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(sorted(self._c.items()))
