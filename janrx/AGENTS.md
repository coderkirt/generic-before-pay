# AGENTS.md (read first)

Project: **JanRx**, a price-clarity tool comparing branded medicines with Jan Aushadhi generics of the same composition.
Full spec: `docs/PRD.md`. Task list: `docs/TASKS.md`. API contract: `docs/API.md`.

## Hard rules (never break)
1. The AI model is used ONLY to read printed text from images. It must never produce dosage, drug facts, uses, warnings, or substitution advice.
2. All medicine facts and prices come from shipped data files in `/data`. If missing: say "Not in our data".
3. No substitution recommendations anywhere. Wording: "A Jan Aushadhi product with the same listed composition is priced at ₹X."
4. The disclaimer must be in every OCR-related and prescription-related response (including errors).
5. Typed entry must always work even if OCR/model is down.
6. No secrets in the repo. Use `.env` (gitignored) and keep `.env.example` current.
7. Never log or store image bytes, extracted text, or patient age/gender.

## Layout
- `backend/` FastAPI service (Python 3.12). `web/` PWA frontend (separate teammate).
- Run: `./start.sh` (Docker) or `./start.sh --local`. Test: `cd backend && pytest`.

## Working style
- Do tasks from `docs/TASKS.md` in order; tick boxes as you finish. Add or update tests with each change.
- Keep functions small and typed. Prefer editing existing modules over adding new ones.
