import asyncio
import io
import os
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings
from app.main import create_app
from app.ocr.base import OcrResult

FIX = Path(__file__).parent / "fixtures"


def make_client(provider=None, **overrides) -> TestClient:
    cfg = dict(ocr_provider="mock", data_dir=str(FIX), ocr_rate_limit_per_minute=100)
    cfg.update(overrides)
    return TestClient(create_app(Settings(_env_file=None, **cfg), ocr_provider=provider))


def png_bytes(noise: bool = False, size=(120, 80)) -> bytes:
    img = Image.frombytes("RGB", size, os.urandom(size[0] * size[1] * 3)) if noise else Image.new("RGB", size, "white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def post_image(client, data: bytes | None = None, filename="box.png", ctype="image/png", **form):
    return client.post("/v1/ocr", files={"file": (filename, data if data is not None else png_bytes(), ctype)}, data=form)


class FakeProvider:
    name = "fake"

    def __init__(self, text="DOLO 650 Tablets", candidates=("DOLO 650",), exc=None, delay=0.0):
        self.text, self.candidates, self.exc, self.delay = text, list(candidates), exc, delay

    async def extract(self, image, mime, language, **_kw):
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.exc:
            raise self.exc
        return OcrResult(text=self.text, candidates=self.candidates, provider=self.name)

    async def check(self):
        return self.exc is None
