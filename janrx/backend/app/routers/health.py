from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}


@router.get("/readyz")
async def readyz(request: Request):
    provider = request.app.state.ocr_provider
    if provider.name == "mock":
        ocr = "mock"
    else:
        ocr = "ok" if await provider.check() else "unavailable"
    data = request.app.state.data.status()
    status = "ready" if ocr in ("ok", "mock") and all(data.values()) else "degraded"
    # Always HTTP 200 while the process is up: OCR being down must not take the typing path offline.
    return {"status": status, "ocr": ocr, "data": data, "typing_path": "available"}
