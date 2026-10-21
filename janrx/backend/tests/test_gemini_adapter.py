import asyncio
import json

import httpx
import pytest

from app.config import Settings
from app.ocr.base import OcrBadOutput, OcrTimeout, OcrUnavailable
from app.ocr.gemini import GeminiOcrProvider

S = Settings(_env_file=None, ocr_provider="gemini", gemini_api_key="test-key", gemini_model="gemini-3.5-flash-lite")


def provider(handler):
    return GeminiOcrProvider(S, transport=httpx.MockTransport(handler))


def gemini_body(text: str):
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


def run(p):
    return asyncio.run(p.extract(b"img", "image/jpeg", "en"))


def test_extracts_json_from_gemini_parts():
    r = run(provider(lambda req: httpx.Response(200, json=gemini_body('{"text":"DOLO 650","candidates":["DOLO 650"]}'))))
    assert r.text == "DOLO 650" and r.candidates == ["DOLO 650"] and r.provider == "gemini" and r.mock is False


def test_sends_inline_image_and_ocr_prompt():
    seen = {}

    def handler(req):
        seen["url"] = str(req.url)
        seen["key"] = req.headers.get("x-goog-api-key")
        seen["body"] = json.loads(req.content)
        return httpx.Response(200, json=gemini_body('{"text":"","candidates":[]}'))

    run(provider(handler))
    assert seen["key"] == "test-key"
    assert seen["url"].endswith("/models/gemini-3.5-flash-lite:generateContent")
    parts = seen["body"]["contents"][0]["parts"]
    assert parts[0]["inlineData"]["mimeType"] == "image/jpeg"
    assert "Do NOT output dosage" in parts[1]["text"]
    assert seen["body"]["generationConfig"]["temperature"] == 0


def test_missing_key_is_unavailable():
    p = GeminiOcrProvider(Settings(_env_file=None, gemini_api_key=""), transport=httpx.MockTransport(lambda r: httpx.Response(200)))
    with pytest.raises(OcrUnavailable):
        run(p)


def test_http_error_is_unavailable():
    with pytest.raises(OcrUnavailable):
        run(provider(lambda req: httpx.Response(403)))


def test_timeout():
    def handler(req):
        raise httpx.ReadTimeout("slow")
    with pytest.raises(OcrTimeout):
        run(provider(handler))


def test_bad_shape():
    with pytest.raises(OcrBadOutput):
        run(provider(lambda req: httpx.Response(200, json={"nope": 1})))
