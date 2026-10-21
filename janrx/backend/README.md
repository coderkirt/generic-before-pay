# JanRx backend (FastAPI)

AI/OCR, security and ops layer. Read `../AGENTS.md` for the safety rules first.

## Run
```bash
../start.sh            # Docker (from repo root; Git Bash / WSL)
../start.ps1           # Windows PowerShell
../start.sh --local    # local venv
../start.ps1 --local
pytest                 # mocked tests, no network or model needed
```

## Model / runtime (BE-2)

Recorded for the default demo stack. Replace the latency row after you measure on the demo laptop.

| Field | Value |
| --- | --- |
| Runtime | Ollama 0.6+ (OpenAI-compatible `POST /v1/chat/completions`) |
| Model id | `gemma4:e4b` (Gemma 4 E4B, multimodal / vision) |
| Size | ~4.5B effective parameters (~8B with embeddings); Ollama download ~6.6–9.5 GB |
| Quantisation | Ollama default GGUF quant for this tag (check `ollama show gemma4:e4b`) |
| Licence | [Gemma Terms of Use](https://ai.google.dev/gemma/terms) (Gemma 4). Review before any public demo or redistribution. |
| Hardware | CPU is possible but slow; a laptop GPU / 16 GB RAM is the intended demo box |
| Measured latency | **TODO — fill after 10-box eval on the demo machine** (p50 / p95, warm vs cold) |
| Endpoint | `GEMMA_BASE_URL` default `http://host.docker.internal:11434/v1` from Docker, or `http://localhost:11434/v1` locally |

Pull and smoke-test:

```bash
ollama pull gemma4:e4b
ollama run gemma4:e4b ./path/to/printed-strip.jpg "Read the printed text. Output JSON only: {\"text\":\"...\",\"candidates\":[...]}"
```

Then set `OCR_PROVIDER=gemma` in `.env`. If Ollama is not installed, keep `OCR_PROVIDER=mock`.

vLLM / llama.cpp also work if they expose the same chat-completions + image_url shape. Change `GEMMA_BASE_URL` and `GEMMA_MODEL` only.

The API container does **not** bundle weights. Gemma 4 E2B is not the default: some runtimes treat it as text-only.

## Gemini instead of Ollama

Set `OCR_PROVIDER=gemini` and `GEMINI_API_KEY` (Google AI Studio). Default model `gemini-3.5-flash-lite`. Same OCR contract: `text` + `candidates` only, same output guard.

**Privacy:** the photo is sent to Google. Do not use this for a real patient sheet unless the UI says so. Local options remain `rapidocr` (no cloud) and `gemma` (Ollama).

### 10-box accuracy report

Drop printed-box / strip photos (no patient identifiers) in `backend/evals/boxes/` and run:

```bash
cd backend
python scripts/ocr_eval.py --base-url http://localhost:8000 --images evals/boxes
```

The script writes `evals/report.json`. Handwriting is unsupported. Fill the table in `evals/boxes/README.md`; do not invent scores.

## Prompt / job
- One job: read visible printed text from a medicine box, strip, or printed prescription.
- Prompt (see `app/ocr/gemma.py::PROMPT`): JSON `{"text", "candidates"}` only; copy exactly; no spelling correction; no dosage, uses, warnings, prices, alternatives or advice.
- `temperature=0`, `think=false`. Image part is sent before the text part. Optional `language` hint is passed through.
- Parser accepts fenced JSON, `<think>` wrappers, and extra prose. Extra keys are ignored. `sanitize_candidates` then keeps only short plain names that literally appear in `text`.
- Candidates are NOT verified drug matches. The frontend must run its fuzzy matcher and require user confirmation.

## Fallback behaviour
Model down -> `503 OCR_UNAVAILABLE`; slow -> `504 OCR_TIMEOUT`; unusable output -> `502 OCR_BAD_OUTPUT`. Each has `fallback: "manual_entry"` and the disclaimer. `/readyz` reports `degraded` but stays HTTP 200, and typing keeps working. `OCR_PROVIDER=mock` returns one of several fixed outputs flagged `mock: true`.

## Privacy (for FE-2 copy)

Exact UI sentence to use:

> Your photo is sent to our server only to read the text and is not stored.

Images stay in memory, are not written to disk, and are discarded when the request ends. Logs never include image bytes, OCR text, age, or gender. Tesseract.js on the client is the true on-device option; the Gemma path is server-side.

## Security and ops
Upload limits (Content-Length check, streamed size cap, magic bytes, Pillow verify, pixel cap), request timeout, CORS allow-list (no `*` in prod), in-memory per-client rate limit (use Redis or a single replica for multi-instance), `X-Request-ID`, JSON logs without PII, in-memory metrics at `/v1/metrics`, non-root Docker user, read-only root filesystem, no secrets in the repo.

Reverse proxy: terminate TLS in front of `:8000`, set `CORS_ORIGINS` to the PWA origin, and only then set `TRUST_PROXY=true` so rate limits use `X-Forwarded-For`. Never expose the API with `TRUST_PROXY=true` on a public port.

Prod: `APP_ENV=prod` hides `/docs` and `/openapi.json`, and refuses `CORS_ORIGINS=*`.

## Handwriting (best-effort)

Port of the Doctor's Prescription OpenCV pipeline (`POST /v1/ocr` with `handwriting=true`):

1. Contrast / CLAHE / Otsu threshold  
2. Contours grouped into words  
3. EMNIST TFLite character CNN (`app/ocr/models/handwriting.tflite`)  
4. Optional Gemini/Gemma second pass  

Handwriting is **not** a promised capability. The response `notice` says to check every item. Typed entry always works.

## Limitations
- Printed text is the supported path. Handwriting is best-effort and often wrong.
- Latin-script candidates only; other scripts may appear in `text` but are dropped from `candidates`.
- Blur, glare, curved packaging and small print reduce accuracy. A vision model can still misread characters, so user confirmation is mandatory.
- Rate limiter and metrics reset on restart and are per-process.
- Data-backed endpoints need `/data/*.json` (not included; see `../data/README.md`).

## Credits
- Gemma is developed by Google DeepMind; use is subject to the Gemma Terms of Use.
- Libraries: FastAPI, Starlette, Pydantic, httpx, Pillow, RapidFuzz, Uvicorn.
- Data sources to be cited once added: PMBJP/BPPI product list, NPPA ceiling prices.
