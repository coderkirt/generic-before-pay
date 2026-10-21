from dataclasses import dataclass
from typing import Protocol


class OcrError(Exception):
    code = "OCR_ERROR"


class OcrUnavailable(OcrError):
    code = "OCR_UNAVAILABLE"


class OcrTimeout(OcrError):
    code = "OCR_TIMEOUT"


class OcrBadOutput(OcrError):
    code = "OCR_BAD_OUTPUT"


@dataclass
class OcrResult:
    text: str
    candidates: list[str]
    provider: str
    mock: bool = False


class OcrProvider(Protocol):
    name: str

    async def extract(self, image: bytes, mime: str, language: str) -> OcrResult: ...

    async def check(self) -> bool:
        """Cheap reachability check for /readyz."""
        ...
