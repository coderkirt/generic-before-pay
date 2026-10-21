import json
from pathlib import Path
from typing import Any

from .errors import ApiError

FILES = ("brands", "janaushadhi_products", "kendras")


class DataStore:
    def __init__(self, data_dir: str) -> None:
        self.dir = Path(data_dir)
        self._cache: dict[str, list[dict[str, Any]]] = {}

    def status(self) -> dict[str, bool]:
        return {name: (self.dir / f"{name}.json").is_file() for name in FILES}

    def load(self, name: str) -> list[dict[str, Any]]:
        if name not in self._cache:
            path = self.dir / f"{name}.json"
            if not path.is_file():
                raise ApiError(503, "DATA_NOT_LOADED",
                               f"The {name} dataset is not available on this server. Not in our data.",
                               fallback="manual_entry")
            self._cache[name] = json.loads(path.read_text(encoding="utf-8"))
        return self._cache[name]
