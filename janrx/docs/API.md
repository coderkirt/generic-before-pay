# API contract (v1)

All JSON responses carry `request_id`. OCR/prescription responses (including errors) carry `disclaimer`.
Every response has an `X-Request-ID` header. Send your own (8-64 chars `[A-Za-z0-9_-]`) to correlate.

## Error envelope
```json
{ "request_id": "…", "error": { "code": "OCR_UNAVAILABLE", "message": "…", "fallback": "manual_entry" }, "disclaimer": "…" }
```
| HTTP | code | meaning |
|---|---|---|
| 400 | INVALID_LANGUAGE / CONFIRMATION_REQUIRED | bad input |
| 413 | FILE_TOO_LARGE / IMAGE_TOO_LARGE | size or pixel limit |
| 415 | UNSUPPORTED_IMAGE | not JPEG/PNG/WebP or corrupt |
| 422 | VALIDATION_ERROR | schema problem |
| 429 | RATE_LIMITED | see `Retry-After` |
| 502 | OCR_BAD_OUTPUT | model returned unusable output |
| 503 | OCR_UNAVAILABLE / DATA_NOT_LOADED | model or data missing; use typing |
| 504 | OCR_TIMEOUT | model too slow; use typing |

## GET /healthz
`{"status":"ok"}`

## GET /readyz
Always 200 while the process is up.
```json
{ "status": "ready|degraded", "ocr": "ok|mock|unavailable", "data": {"brands": true, "janaushadhi_products": false, "kendras": false}, "typing_path": "available" }
```

## POST /v1/ocr  (multipart/form-data)
Fields: `file` (JPEG/PNG/WebP, <= `OCR_MAX_BYTES`), `language` (optional, default `en`), `preprocess` (optional bool, default true), `handwriting` (optional bool, default false).

Set `handwriting=true` for a doctor's handwritten pad. That runs the OpenCV + EMNIST character pipeline (from the Doctor's Prescription project) and, if configured, Gemini/Gemma as a second reader. Printed-box preprocess is skipped. The `notice` then warns that handwriting is best-effort.
```json
{
  "request_id": "…", "text": "DOLO 650 TABLETS …", "candidates": ["DOLO 650"],
  "language": "en", "provider": "gemma", "mock": false, "preprocessed": true,
  "notice": "Candidates are text read from the image, not verified matches. Please check each one.",
  "disclaimer": "…"
}
```
`candidates` are names found in the image text only. They are NOT drug facts. The frontend must run them through its fuzzy matcher and let the user confirm.

## POST /v1/prescription/candidates
Body: `{ "items": ["Pantocid40", "Crosin"] }` -> per item `tier` (`exact|likely|uncertain|none`), `reason`, `matches[{brand_id, brand_name, composition_id, score}]`, `verify_notice`. No prices here.

## POST /v1/prescription/summary
Body:
```json
{ "patient": {"age_years": 34, "gender": "female"}, "confirmed_by_user": true,
  "items": [{"brand_id": "…", "quantity_packs": 1}] }
```
Returns per-line comparison and totals. Only lines with status `compared` count toward totals. Requires `confirmed_by_user: true` (else 400).

## GET /v1/kendras/nearest?lat=..&lng=..&limit=3
Nearest Kendras with `distance_km`, address, and a maps link. 503 `DATA_NOT_LOADED` if `kendras.json` is absent.

## GET /v1/metrics
In-memory counters (requests by route/status, OCR successes/failures by code). No personal data. Resets on restart.
