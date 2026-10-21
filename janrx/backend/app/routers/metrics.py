from fastapi import APIRouter, Request

router = APIRouter(prefix="/v1", tags=["ops"])


@router.get("/metrics")
async def metrics(request: Request):
    return {"counters": request.app.state.metrics.snapshot()}
