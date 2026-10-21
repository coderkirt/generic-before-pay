"""On-device printed-text OCR (RapidOCR / ONNX). Used when Ollama/Gemma is not installed.

Still a TEXT READER only. Candidates go through sanitize_candidates like Gemma output.
"""
import asyncio
import io
import re

from PIL import Image

from .base import OcrResult, OcrUnavailable

_SKIP = re.compile(
    r"^(dose|frequency|duration|remarks|medications|prescription|advice|tablet|capsule|"
    r"symptoms|diagnosis|after meal|empty stomach|breakfast|week|weeks|days|sos|"
    r"followup|follow-up)$",
    re.I,
)


class RapidOcrProvider:
    name = "rapidocr"

    def __init__(self) -> None:
        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
            except ImportError as exc:
                raise OcrUnavailable("RapidOCR is not installed") from exc
            self._engine = RapidOCR()
        return self._engine

    def _extract_sync(self, image: bytes) -> OcrResult:
        import numpy as np

        engine = self._get_engine()
        img = Image.open(io.BytesIO(image)).convert("RGB")
        result, _elapse = engine(np.array(img))
        lines = [item[1] for item in (result or []) if isinstance(item, (list, tuple)) and len(item) > 1]
        text = "\n".join(lines)
        cands = [ln.strip() for ln in lines if ln.strip() and not _SKIP.match(ln.strip())]
        return OcrResult(text=text, candidates=cands, provider=self.name, mock=False)

    async def extract(self, image: bytes, mime: str, language: str, **_kw) -> OcrResult:
        try:
            return await asyncio.to_thread(self._extract_sync, image)
        except OcrUnavailable:
            raise
        except Exception as exc:
            raise OcrUnavailable("Local OCR failed") from exc

    async def check(self) -> bool:
        try:
            self._get_engine()
        except OcrUnavailable:
            return False
        return True
