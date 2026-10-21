# TASKS (Backend Member 2: AI/OCR, Security and Ops)

Status key: [x] scaffolded in this repo, [ ] for Cursor to complete/verify. Work top to bottom.

## Core
- [x] FastAPI skeleton (`backend/app/main.py`, `create_app` factory)
- [x] `GET /healthz` (liveness) and `GET /readyz` (readiness; reports degraded if OCR is down, typing path stays available)
- [x] `POST /v1/ocr`: Gemma OCR for printed boxes/strips; returns `text` + `candidates` only
- [x] Output guard: no dosage/facts/substitution; candidates must appear in the extracted text
- [x] Fallback: model down/timeout/bad output -> clear error with `fallback: "manual_entry"`
- [x] Upload limits: Content-Length check, streamed size cap, magic-byte check, Pillow verify, pixel cap, timeout
- [x] CORS via `CORS_ORIGINS` (no wildcard in prod)
- [x] Rate limit on `/v1/ocr` (sliding window, 429 + Retry-After)
- [x] Request IDs (`X-Request-ID`) + JSON structured logs
- [x] Disclaimer in every OCR-related response, including errors
- [x] Dockerfile, docker-compose, `start.sh`
- [x] `.env.example`, `.gitignore`, no secrets
- [x] Mocked tests: OCR success, failure, timeout, fallback, limits, rate limit
- [x] Fill in README "Model/Runtime" with the Gemma 4 E4B / Ollama default (id, size, licence). **Still need:** 10 real printed boxes/strips + measured latency on the demo machine (`backend/evals/boxes/`)
- [x] Tune `GEMMA_MODEL`/prompt in `backend/app/ocr/gemma.py` (JSON buried in prose/`<think>`, image-before-text, `think=false`). Re-tune if a live eval shows a new wrapper.

## Optional
- [x] `POST /v1/prescription/candidates` + `POST /v1/prescription/summary` (requires `confirmed_by_user: true`)
- [x] `GET /v1/kendras/nearest` (nearest 3 with distance)
- [x] Image pre-processing (`app/ocr/service.py::preprocess_image`)
- [x] Language hint (`language` form field)
- [x] `GET /v1/metrics` basic counters
- [x] Mock mode (`OCR_PROVIDER=mock`), responses flagged `mock: true`
- [ ] Populate `/data` with curated, cited datasets (see PRD section 8). Run the validator once written (`scripts/validate_data.py`, TODO) — **BE-1**
- [ ] Hindi disclaimer copy (needs human review, not machine-generated)
- [ ] Redis-backed rate limiter if running more than one instance (single replica is enough for demo; documented in README)
- [x] CI (`pytest`) + demo-day runbook (`docs/RUNBOOK.md`) + Windows `start.ps1`
- [x] Handwriting best-effort: OpenCV + EMNIST TFLite from doctors-prescription, `handwriting=true` on `POST /v1/ocr`

## Definition of done
- `./start.sh` brings the API up; `curl localhost:8000/readyz` works.
- `cd backend && pytest -q` is green.
- With the model stopped, `/v1/ocr` returns 503 `OCR_UNAVAILABLE` with the disclaimer and `fallback: manual_entry`.
- With `OCR_PROVIDER=mock`, the demo flow works end to end.
