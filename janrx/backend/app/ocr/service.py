"""Image validation, pre-processing and output sanitising for OCR."""
import io
import re

from fastapi import UploadFile
from PIL import Image, ImageFilter, ImageOps

from ..errors import ApiError


def sniff_mime(data: bytes) -> str | None:
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


async def read_limited(file: UploadFile, max_bytes: int) -> bytes:
    chunks, total = [], 0
    while chunk := await file.read(64 * 1024):
        total += len(chunk)
        if total > max_bytes:
            raise ApiError(413, "FILE_TOO_LARGE", f"Image is larger than {max_bytes // (1024 * 1024)} MB. Please use a smaller photo.",
                           fallback="manual_entry")
        chunks.append(chunk)
    return b"".join(chunks)


def validate_image(data: bytes, max_pixels: int) -> str:
    mime = sniff_mime(data)
    if mime is None:
        raise ApiError(415, "UNSUPPORTED_IMAGE", "Please upload a JPEG, PNG or WebP photo.", fallback="manual_entry")
    try:
        img = Image.open(io.BytesIO(data))
        w, h = img.size
        if w * h > max_pixels:
            raise ApiError(413, "IMAGE_TOO_LARGE", "Image resolution is too high. Please use a smaller photo.",
                           fallback="manual_entry")
        img.verify()
    except ApiError:
        raise
    except Exception as exc:  # corrupt or malicious image
        raise ApiError(415, "UNSUPPORTED_IMAGE", "That image could not be read.", fallback="manual_entry") from exc
    return mime


def preprocess_image(data: bytes, max_side: int = 1600) -> tuple[bytes, str]:
    """Grayscale, fix rotation, autocontrast, downscale, light sharpen. Returns (jpeg_bytes, mime)."""
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(data)))
    img = ImageOps.autocontrast(img.convert("L"))
    if max(img.size) > max_side:
        img.thumbnail((max_side, max_side), Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=3))
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=90)
    return out.getvalue(), "image/jpeg"


_ALLOWED = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 .+\-/()%]{1,59}$")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower()).strip()


def sanitize_candidates(text: str, candidates: list[str], limit: int = 30) -> list[str]:
    """Keep only short, plain-looking names that literally appear in the extracted text.
    This is the anti-hallucination guard: do not loosen it."""
    norm_text, out, seen = _norm(text), [], set()
    for c in candidates:
        if not isinstance(c, str):
            continue
        c = re.sub(r"\s+", " ", c).strip()
        n = _norm(c)
        if not _ALLOWED.match(c) or n in seen or n not in norm_text:
            continue
        seen.add(n)
        out.append(c)
        if len(out) >= limit:
            break
    return out


def build_provider(settings):
    from .gemma import GemmaOcrProvider
    from .gemini import GeminiOcrProvider
    from .mock import MockOcrProvider
    from .rapid import RapidOcrProvider
    name = settings.ocr_provider.lower()
    if name == "mock":
        return MockOcrProvider()
    if name in ("rapidocr", "rapid", "local"):
        return RapidOcrProvider()
    if name == "gemini":
        return GeminiOcrProvider(settings)
    if name in ("handwriting", "emnist"):
        from .handwriting import HandwritingOcrProvider
        fallback = GeminiOcrProvider(settings) if settings.gemini_api_key else None
        return HandwritingOcrProvider(fallback=fallback)
    return GemmaOcrProvider(settings)
