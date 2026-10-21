from dataclasses import replace
from zlib import crc32

from .base import OcrResult

# Several fixed demo prescriptions. The image is never read.
_SAMPLES = (
    OcrResult(text="MOCK OCR OUTPUT\nDOLO 650\nTablets", candidates=["DOLO 650"], provider="mock", mock=True),
    OcrResult(text="MOCK OCR OUTPUT\nPANTOCID 40\nTablets", candidates=["PANTOCID 40"], provider="mock", mock=True),
    OcrResult(text="MOCK OCR OUTPUT\nCROCIN ADVANCE\nParacetamol", candidates=["CROCIN ADVANCE"], provider="mock", mock=True),
    OcrResult(text="MOCK OCR OUTPUT\nGLYCOMET 500\nTablets", candidates=["GLYCOMET 500"], provider="mock", mock=True),
)


class MockOcrProvider:
    """Deterministic demo mode. Does NOT read the image. Responses are flagged mock=true."""

    name = "mock"

    async def extract(self, image: bytes, mime: str, language: str, **_kw) -> OcrResult:
        sample = _SAMPLES[crc32(image) % len(_SAMPLES)]
        return replace(sample)

    async def check(self) -> bool:
        return True
