"""
backend/main.py

FastAPI application for Generic Before Pay.
Provides REST endpoints:
- GET  /api/v1/search
- GET  /api/v1/drugs/{id}
- POST /api/v1/compare
- GET  /api/v1/data/version
- GET  /api/v1/data/bundle

Strict safety rules:
- Disclaimer in every response.
- No medical dosage, frequency, or substitution advice.
- Structured logs for search queries and not-found cases.
"""

import json
import logging
import hashlib
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from backend.database import init_db, DEFAULT_SEED_PATH
from backend.dal import (
    get_drug_by_id,
    get_all_drugs,
    search_drugs,
    get_dataset_metadata,
    calculate_compare,
    STANDARD_DISCLAIMER
)
from backend.schemas import (
    SearchResponse,
    SearchData,
    SearchMatchItem,
    DrugDetailResponse,
    DrugDetailData,
    CompareRequest,
    CompareResponse,
    CompareData,
    DataVersionResponse,
    DataVersionData,
    DataBundleResponse,
    DataBundleMetadata,
    ErrorResponse
)

# Setup structured logger
logger = logging.getLogger("generic_before_pay")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": %(message)s}'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def _log_event(event_type: str, **kwargs):
    payload = {"event": event_type, **kwargs}
    logger.info(json.dumps(payload))


def compute_dataset_hash() -> str:
    if DEFAULT_SEED_PATH.exists():
        with open(DEFAULT_SEED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')
        return hashlib.sha256(canonical_json).hexdigest()
    return "unknown"


DATASET_HASH = compute_dataset_hash()
DATASET_VERSION = "2026.10.1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB on startup
    init_db()
    _log_event("app_startup", version=DATASET_VERSION, dataset_hash=DATASET_HASH)
    yield


app = FastAPI(
    title="Generic Before Pay API",
    description="Cost-transparency and generic medicine alternatives lookup.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters or payload",
                "details": exc.errors()
            },
            "disclaimer": STANDARD_DISCLAIMER
        }
    )


# Global HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = "RESOURCE_NOT_FOUND" if exc.status_code == 404 else "CLIENT_ERROR"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": exc.detail,
                "details": None
            },
            "disclaimer": STANDARD_DISCLAIMER
        }
    )


from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/search", response_model=SearchResponse)
def search_drugs_endpoint(
    q: str = Query(..., min_length=1, description="Drug brand name, partial name, or molecule"),
    limit: int = Query(3, ge=1, le=10, description="Max matches to return (default 3)")
):
    query_str = q.strip()
    matches = search_drugs(query=query_str, limit=limit)

    _log_event(
        "search_query",
        query=query_str,
        results_count=len(matches),
        top_match=matches[0]["brand_name"] if matches else None,
        top_confidence=matches[0]["confidence_score"] if matches else 0.0
    )

    if not matches:
        _log_event("search_not_found", query=query_str)

    match_items = [SearchMatchItem(**m) for m in matches]
    return SearchResponse(
        success=True,
        data=SearchData(
            query=query_str,
            total_matches=len(match_items),
            matches=match_items
        ),
        disclaimer=STANDARD_DISCLAIMER
    )


@api_router.get("/drugs/{id}", response_model=DrugDetailResponse)
def get_drug_detail_endpoint(id: str):
    drug = get_drug_by_id(id)
    if not drug:
        _log_event("drug_detail_not_found", requested_id=id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drug with id '{id}' was not found."
        )

    return DrugDetailResponse(
        success=True,
        data=DrugDetailData(**drug),
        disclaimer=STANDARD_DISCLAIMER
    )


@api_router.post("/compare", response_model=CompareResponse)
def compare_drugs_endpoint(payload: CompareRequest):
    items = [{"id": it.id, "quantity": it.quantity} for it in payload.items]
    result = calculate_compare(items)
    
    _log_event(
        "compare_basket",
        item_count=len(payload.items),
        total_savings=result["summary"]["total_savings"]
    )

    return CompareResponse(
        success=True,
        data=CompareData(
            summary=result["summary"],
            breakdown=result["breakdown"]
        ),
        disclaimer=STANDARD_DISCLAIMER
    )


@api_router.get("/data/version", response_model=DataVersionResponse)
def get_data_version_endpoint():
    meta = get_dataset_metadata()
    return DataVersionResponse(
        success=True,
        data=DataVersionData(
            schema_version="1.0.0",
            dataset_version=DATASET_VERSION,
            dataset_hash=meta.get("dataset_hash", DATASET_HASH),
            total_records=int(meta.get("total_records", 0))
        )
    )


@api_router.get("/data/bundle", response_model=DataBundleResponse)
def get_data_bundle_endpoint(request: Request, response: Response):
    client_etag = request.headers.get("if-none-match")
    if client_etag and client_etag.strip('"') == DATASET_HASH:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)

    response.headers["ETag"] = f'"{DATASET_HASH}"'
    all_drugs = get_all_drugs()

    return DataBundleResponse(
        success=True,
        metadata=DataBundleMetadata(
            version=DATASET_VERSION,
            dataset_hash=DATASET_HASH,
            record_count=len(all_drugs)
        ),
        drugs=[DrugDetailData(**d) for d in all_drugs],
        disclaimer=STANDARD_DISCLAIMER
    )


# Register routes under both /api/v1 (canonical) and /api (convenience fallback)
app.include_router(api_router, prefix="/api/v1")
app.include_router(api_router, prefix="/api")
