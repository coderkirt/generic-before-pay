from app.config import Settings
from app.ocr.base import OcrBadOutput, OcrTimeout, OcrUnavailable
from app.disclaimer import DISCLAIMER

from tests.conftest import FakeProvider, make_client, png_bytes, post_image


def test_ocr_success_returns_text_and_candidates_only():
    r = post_image(make_client(FakeProvider()), language="hi")
    assert r.status_code == 200
    body = r.json()
    assert body["text"] == "DOLO 650 Tablets"
    assert body["candidates"] == ["DOLO 650"]
    assert body["language"] == "hi" and body["mock"] is False and body["preprocessed"] is True
    assert body["disclaimer"] == DISCLAIMER
    # no drug facts leak through the response model
    assert set(body) == {"request_id", "disclaimer", "text", "candidates", "language", "provider", "mock", "preprocessed", "notice"}


def test_hallucinated_candidates_are_dropped():
    p = FakeProvider(text="DOLO 650 Tablets", candidates=["DOLO 650", "Paracetamol 500mg", "Take twice daily"])
    r = post_image(make_client(p))
    assert r.json()["candidates"] == ["DOLO 650"]


def test_mock_mode_works_and_is_flagged():
    r = post_image(make_client())
    body = r.json()
    assert r.status_code == 200 and body["mock"] is True and body["provider"] == "mock"
    assert body["candidates"] and all(c in body["text"] for c in body["candidates"])


def test_readyz_degraded_when_model_down_keeps_typing_path():
    class Down:
        name = "gemma"

        async def extract(self, image, mime, language):
            raise OcrUnavailable("down")

        async def check(self):
            return False

    c = make_client(Down())
    ready = c.get("/readyz").json()
    assert c.get("/readyz").status_code == 200
    assert ready["status"] == "degraded" and ready["ocr"] == "unavailable"
    assert ready["typing_path"] == "available"
    typed = c.post("/v1/prescription/candidates", json={"items": ["testoprazole 40"]})
    assert typed.status_code == 200


def test_content_length_header_rejected_before_body():
    c = make_client(FakeProvider(), ocr_max_bytes=1000)
    # Real Content-Length (clients recompute the header from the body).
    payload = (
        b"--abc\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.png\"\r\n"
        b"Content-Type: image/png\r\n\r\n" + (b"x" * 200_000) + b"\r\n--abc--\r\n"
    )
    r = c.post("/v1/ocr", content=payload, headers={"content-type": "multipart/form-data; boundary=abc"})
    assert r.status_code == 413 and r.json()["error"]["code"] == "FILE_TOO_LARGE"
    assert r.json()["disclaimer"] == DISCLAIMER


def test_request_id_header_and_echo():
    c = make_client(FakeProvider())
    r = c.post("/v1/ocr", files={"file": ("a.png", png_bytes(), "image/png")}, headers={"X-Request-ID": "abc12345-test"})
    assert r.headers["X-Request-ID"] == "abc12345-test" and r.json()["request_id"] == "abc12345-test"
    r2 = c.get("/healthz", headers={"X-Request-ID": "bad id!"})
    assert r2.headers["X-Request-ID"] != "bad id!" and len(r2.headers["X-Request-ID"]) >= 8


def _assert_fallback(r, status, code):
    assert r.status_code == status
    body = r.json()
    assert body["error"]["code"] == code
    assert body["error"]["fallback"] == "manual_entry"
    assert body["disclaimer"] == DISCLAIMER
    assert body["request_id"]


def test_model_unavailable_falls_back_to_typing():
    c = make_client(FakeProvider(exc=OcrUnavailable("down")))
    _assert_fallback(post_image(c), 503, "OCR_UNAVAILABLE")
    # typing path still works
    ok = c.post("/v1/prescription/candidates", json={"items": ["testoprazole 40"]})
    assert ok.status_code == 200 and ok.json()["results"][0]["tier"] == "exact"
    assert c.get("/readyz").status_code == 200


def test_model_timeout_from_provider():
    _assert_fallback(post_image(make_client(FakeProvider(exc=OcrTimeout("slow")))), 504, "OCR_TIMEOUT")


def test_overall_timeout_enforced():
    c = make_client(FakeProvider(delay=2), ocr_timeout_seconds=0.1)
    _assert_fallback(post_image(c), 504, "OCR_TIMEOUT")


def test_bad_model_output():
    _assert_fallback(post_image(make_client(FakeProvider(exc=OcrBadOutput("x")))), 502, "OCR_BAD_OUTPUT")


def test_unexpected_provider_crash_is_contained():
    _assert_fallback(post_image(make_client(FakeProvider(exc=RuntimeError("boom")))), 503, "OCR_UNAVAILABLE")


def test_file_too_large():
    c = make_client(FakeProvider(), ocr_max_bytes=1000)
    r = post_image(c, png_bytes(noise=True, size=(200, 200)))
    assert r.status_code == 413 and r.json()["error"]["code"] == "FILE_TOO_LARGE"
    assert r.json()["disclaimer"] == DISCLAIMER


def test_pixel_cap():
    c = make_client(FakeProvider(), ocr_max_pixels=100)
    r = post_image(c)
    assert r.status_code == 413 and r.json()["error"]["code"] == "IMAGE_TOO_LARGE"


def test_not_an_image_rejected_despite_content_type():
    r = post_image(make_client(FakeProvider()), b"not an image at all", filename="x.png", ctype="image/png")
    assert r.status_code == 415 and r.json()["error"]["code"] == "UNSUPPORTED_IMAGE"


def test_invalid_language_hint():
    r = post_image(make_client(FakeProvider()), language="english!!")
    assert r.status_code == 400 and r.json()["error"]["code"] == "INVALID_LANGUAGE"


def test_missing_file_validation_error_has_disclaimer():
    r = make_client(FakeProvider()).post("/v1/ocr")
    assert r.status_code == 422 and r.json()["disclaimer"] == DISCLAIMER


def test_rate_limit_and_retry_after():
    c = make_client(FakeProvider(), ocr_rate_limit_per_minute=2)
    assert post_image(c).status_code == 200
    assert post_image(c).status_code == 200
    r = post_image(c)
    assert r.status_code == 429 and int(r.headers["Retry-After"]) >= 1
    assert r.json()["error"]["code"] == "RATE_LIMITED" and r.json()["disclaimer"] == DISCLAIMER


def test_cors_preflight_allows_only_configured_origin():
    c = make_client(cors_origins="https://app.example.test")
    ok = c.options("/v1/ocr", headers={"Origin": "https://app.example.test", "Access-Control-Request-Method": "POST"})
    bad = c.options("/v1/ocr", headers={"Origin": "https://evil.test", "Access-Control-Request-Method": "POST"})
    assert ok.headers.get("access-control-allow-origin") == "https://app.example.test"
    assert "access-control-allow-origin" not in bad.headers


def test_prod_rejects_wildcard_cors():
    import pytest
    with pytest.raises(ValueError):
        Settings(_env_file=None, app_env="prod", cors_origins="*")


def test_metrics_count_without_personal_data():
    c = make_client(FakeProvider())
    post_image(c)
    counters = c.get("/v1/metrics").json()["counters"]
    assert counters["ocr success"] == 1
    assert all("DOLO" not in k for k in counters)


def test_preprocess_can_be_disabled():
    c = make_client(FakeProvider())
    assert post_image(c, preprocess="false").json()["preprocessed"] is False
    assert post_image(c).json()["preprocessed"] is True
