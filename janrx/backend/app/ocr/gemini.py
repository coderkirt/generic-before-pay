"""Google Gemini vision OCR (hosted). Same job as Gemma: read printed text only.

The photo is sent to Google's API and is not stored by JanRx. Do not use this path
for real patient prescriptions unless that disclosure is shown in the UI.
"""
import base64

import httpx

from ..config import Settings
from .base import OcrBadOutput, OcrResult, OcrTimeout, OcrUnavailable
from .gemma import HANDWRITING_PROMPT, PROMPT, parse_model_json


def _response_text(payload: object) -> str:
    try:
        parts = payload["candidates"][0]["content"]["parts"]  # type: ignore[index]
        texts = [p.get("text", "") for p in parts if isinstance(p, dict)]
        return "".join(texts)
    except (TypeError, KeyError, IndexError) as exc:
        raise OcrBadOutput("Unexpected response shape") from exc


class GeminiOcrProvider:
    name = "gemini"

    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self._s = settings
        self._transport = transport

    def _key(self) -> str:
        return (self._s.gemini_api_key or self._s.gemma_api_key or "").strip()

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        key = self._key()
        if key:
            h["x-goog-api-key"] = key
        return h

    def _url(self, suffix: str) -> str:
        base = self._s.gemini_base_url.rstrip("/")
        model = self._s.gemini_model
        return f"{base}/models/{model}:{suffix}"

    async def extract(self, image: bytes, mime: str, language: str, **kwargs) -> OcrResult:
        if not self._key():
            raise OcrUnavailable("GEMINI_API_KEY is not set")
        prompt = HANDWRITING_PROMPT if kwargs.get("handwriting") else PROMPT
        payload = {
            "contents": [{"parts": [
                {"inlineData": {"mimeType": mime, "data": base64.b64encode(image).decode()}},
                {"text": prompt.format(language=language)},
            ]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 800},
        }
        try:
            async with httpx.AsyncClient(transport=self._transport,
                                         timeout=self._s.ocr_timeout_seconds) as client:
                resp = await client.post(self._url("generateContent"), json=payload, headers=self._headers())
        except httpx.TimeoutException as exc:
            raise OcrTimeout("Model timed out") from exc
        except httpx.HTTPError as exc:
            raise OcrUnavailable("Gemini endpoint unreachable") from exc
        if resp.status_code >= 400:
            raise OcrUnavailable(f"Gemini returned {resp.status_code}")
        text, cands = parse_model_json(_response_text(resp.json()))
        return OcrResult(text=text, candidates=cands, provider=self.name)

    async def check(self) -> bool:
        if not self._key():
            return False
        try:
            async with httpx.AsyncClient(transport=self._transport, timeout=2.0) as client:
                r = await client.get(
                    f"{self._s.gemini_base_url.rstrip('/')}/models/{self._s.gemini_model}",
                    headers=self._headers(),
                )
            return r.status_code < 500
        except httpx.HTTPError:
            return False
