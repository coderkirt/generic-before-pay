import asyncio
import logging
import re

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.concurrency import run_in_threadpool

from ..errors import ApiError
from ..ocr.base import OcrBadOutput, OcrError, OcrTimeout, OcrUnavailable
from ..ocr.handwriting import HANDWRITING_NOTICE, HandwritingOcrProvider
from ..ocr.service import preprocess_image, read_limited, sanitize_candidates, validate_image
from ..ratelimit import ocr_rate_limit
from ..schemas import OcrResponse

router = APIRouter(prefix="/v1", tags=["ocr"])
log = logging.getLogger("janrx")
_LANG = re.compile(r"^[a-z]{2,3}(-[A-Za-z]{2,4})?$")

_ERRORS = {
    OcrUnavailable: (503, "OCR_UNAVAILABLE", "Scanning is unavailable right now. You can still type the medicine names."),
    OcrTimeout: (504, "OCR_TIMEOUT", "Scanning took too long. Please try again or type the medicine names."),
    OcrBadOutput: (502, "OCR_BAD_OUTPUT", "We could not read that image reliably. Please try a clearer photo or type the names."),
}


async def enforce_content_length(request: Request) -> None:
    """Reject oversized uploads from the header before the body is parsed."""
    limit = request.app.state.settings.ocr_max_bytes + 64 * 1024  # multipart overhead
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > limit:
        raise ApiError(413, "FILE_TOO_LARGE", "Image is too large. Please use a smaller photo.", fallback="manual_entry")


def _flag(value: str | None) -> bool:
    return bool(value) and value.strip().lower() in ("1", "true", "yes", "on")


@router.post("/ocr", response_model=OcrResponse,
             dependencies=[Depends(ocr_rate_limit), Depends(enforce_content_length)])
async def ocr(request: Request, file: UploadFile = File(...), language: str = Form("en"),
              preprocess: str | None = Form(None), handwriting: str | None = Form(None)) -> OcrResponse:
    s, metrics = request.app.state.settings, request.app.state.metrics
    if not _LANG.match(language):
        raise ApiError(400, "INVALID_LANGUAGE", "Language hint must look like 'en' or 'hi'.")

    hw = _flag(handwriting)
    do_pre = (not hw) and (preprocess is None or preprocess.strip().lower() not in ("false", "0", "no", "off"))
    data = await read_limited(file, s.ocr_max_bytes)
    mime = validate_image(data, s.ocr_max_pixels)
    if do_pre:
        data, mime = await run_in_threadpool(preprocess_image, data)

    provider = request.app.state.ocr_provider
    if hw and provider.name != "handwriting":
        provider = HandwritingOcrProvider(fallback=provider)
    try:
        result = await asyncio.wait_for(
            provider.extract(data, mime, language, handwriting=hw), timeout=s.ocr_timeout_seconds)
    except asyncio.TimeoutError as exc:
        err: OcrError = OcrTimeout("timeout")
        err.__cause__ = exc
    except OcrError as e:
        err = e
    except Exception as exc:  # provider bug: still degrade gracefully
        err = OcrUnavailable("provider error")
        err.__cause__ = exc
    else:
        metrics.inc("ocr success")
        candidates = sanitize_candidates(result.text, result.candidates)
        log.info("ocr_ok", extra={"fields": {"provider": result.provider, "mock": result.mock,
                                             "text_chars": len(result.text), "candidates": len(candidates)}})
        notice = HANDWRITING_NOTICE if hw else OcrResponse.model_fields["notice"].default
        return OcrResponse(text=result.text, candidates=candidates, language=language,
                           provider=result.provider, mock=result.mock, preprocessed=do_pre,
                           notice=notice)

    status, code, message = next((v for k, v in _ERRORS.items() if isinstance(err, k)),
                                 (503, "OCR_UNAVAILABLE", _ERRORS[OcrUnavailable][2]))
    metrics.inc(f"ocr failure {code}")
    log.warning("ocr_failed", extra={"fields": {"code": code, "error_type": type(err.__cause__ or err).__name__}})
    raise ApiError(status, code, message, fallback="manual_entry")
