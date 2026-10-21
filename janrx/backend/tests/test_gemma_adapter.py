import asyncio
import json

import httpx
import pytest

from app.config import Settings
from app.ocr.base import OcrBadOutput, OcrTimeout, OcrUnavailable
from app.ocr.gemma import GemmaOcrProvider, PROMPT, parse_model_json

S = Settings(_env_file=None, ocr_provider="gemma", gemma_base_url="http://model.test/v1", gemma_model="m")


def provider(handler):
    return GemmaOcrProvider(S, transport=httpx.MockTransport(handler))


def reply(content):
    return lambda req: httpx.Response(200, json={"choices": [{"message": {"content": content}}]})


def run(p):
    return asyncio.run(p.extract(b"img", "image/jpeg", "en"))


def test_parses_json_in_code_fence():
    r = run(provider(reply('```json\n{"text": "DOLO 650", "candidates": ["DOLO 650"]}\n```')))
    assert r.text == "DOLO 650" and r.candidates == ["DOLO 650"] and r.provider == "gemma"


def test_parses_json_buried_in_prose_and_think_tags():
    wrapped = '<think>plan</think> Here you go:\n{"text": "DOLO 650", "candidates": ["DOLO 650"], "advice": "take twice"}\nThanks'
    r = run(provider(reply(wrapped)))
    assert r.text == "DOLO 650" and r.candidates == ["DOLO 650"]


def test_parses_multipart_message_content():
    content = [{"type": "text", "text": '{"text": "DOLO 650", "candidates": ["DOLO 650"]}'}]
    r = run(provider(lambda req: httpx.Response(200, json={"choices": [{"message": {"content": content}}]})))
    assert r.candidates == ["DOLO 650"]


def test_request_is_deterministic_and_sends_image():
    seen = {}

    def handler(req):
        seen.update(json.loads(req.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"text":"","candidates":[]}'}}]})

    run(provider(handler))
    assert seen["temperature"] == 0 and seen["model"] == "m" and seen["think"] is False
    parts = seen["messages"][0]["content"]
    assert parts[0]["image_url"]["url"].startswith("data:image/jpeg;base64,")
    assert "Do NOT output dosage" in parts[1]["text"] and "substitut" not in PROMPT.lower()


@pytest.mark.parametrize("content", ["just prose", '{"text": 5, "candidates": []}', '{"text": "x"}', "[]"])
def test_non_conforming_output_raises_bad_output(content):
    with pytest.raises(OcrBadOutput):
        run(provider(reply(content)))


def test_weird_response_shape():
    with pytest.raises(OcrBadOutput):
        run(provider(lambda req: httpx.Response(200, json={"nope": 1})))


def test_connection_error_is_unavailable():
    def handler(req):
        raise httpx.ConnectError("refused")
    with pytest.raises(OcrUnavailable):
        run(provider(handler))


def test_http_error_status_is_unavailable():
    with pytest.raises(OcrUnavailable):
        run(provider(lambda req: httpx.Response(500)))


def test_read_timeout_maps_to_timeout():
    def handler(req):
        raise httpx.ReadTimeout("slow")
    with pytest.raises(OcrTimeout):
        run(provider(handler))


def test_check_reflects_reachability():
    assert asyncio.run(provider(lambda r: httpx.Response(200, json={})).check()) is True

    def down(req):
        raise httpx.ConnectError("x")
    assert asyncio.run(provider(down).check()) is False


def test_parse_model_json_direct():
    assert parse_model_json('{"text":"a","candidates":["b",3]}') == ("a", ["b"])
