# Demo-day runbook (BE-2)

## Default: mock (safest)

1. From the repo root: `./start.sh` or `.\start.ps1` (first run copies `.env` with `OCR_PROVIDER=mock`).
2. Check `curl http://localhost:8000/readyz` — expect `"ocr": "mock"`, `"typing_path": "available"`.
3. Frontend: scan any image. UI must show a **Demo mode** badge because `mock: true`.
4. If Docker is unavailable, `./start.sh --local` / `.\start.ps1 --local`.

## Real Gemma (optional)

1. Install [Ollama](https://ollama.com), then `ollama pull gemma4:e4b`.
2. In `.env`: `OCR_PROVIDER=gemma`, `GEMMA_MODEL=gemma4:e4b`, `GEMMA_BASE_URL=http://host.docker.internal:11434/v1` (Docker) or `http://localhost:11434/v1` (local).
3. Restart the API. `/readyz` should show `"ocr": "ok"` once Ollama answers `/v1/models`.
4. Scan a **printed** box or strip. Treat every candidate as unverified.

If Ollama is slow or missing RAM, switch back to mock immediately. Do not debug the model live in front of judges.

## Fallback rehearsal (do this the night before)

1. With `OCR_PROVIDER=gemma`, stop Ollama (`ollama stop` or quit the app).
2. `POST /v1/ocr` must return **503** `OCR_UNAVAILABLE`, `fallback: "manual_entry"`, and the disclaimer.
3. `GET /readyz` stays **200** with `status: degraded` and `typing_path: available`.
4. Typed entry / prescription candidates still work.
5. Restart Ollama or set `OCR_PROVIDER=mock`.

## If something breaks on stage

| Symptom | Action |
| --- | --- |
| Scan hangs | Cancel in the UI; type names. Check `OCR_TIMEOUT_SECONDS`. |
| 429 | Wait for `Retry-After`, or type names. |
| CORS errors | `CORS_ORIGINS` must be the exact PWA origin (scheme + host + port). |
| Port 8000 busy | Stop the other process or change the compose port mapping. |
| Docs 404 | That is correct in `APP_ENV=prod`. |

## Do not

- Log or show raw prescription photos.
- Let the model invent uses, doses, or “switch to generic”.
- Claim handwriting works.
- Set `CORS_ORIGINS=*` or `TRUST_PROXY=true` on a public demo network.
