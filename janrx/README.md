# JanRx

Compare a prescribed brand with the Jan Aushadhi product of the same listed composition. Price and composition information only, not medical advice.

- Product spec: [docs/PRD.md](docs/PRD.md)  - Cursor task list: [docs/TASKS.md](docs/TASKS.md)  - API: [docs/API.md](docs/API.md)
- Backend details (model, runtime, limits, credits): [backend/README.md](backend/README.md)

## Run
```bash
./start.sh            # Docker, one command (creates .env with OCR_PROVIDER=mock on first run)
./start.sh --local    # no Docker
.\start.ps1           # Windows PowerShell
```
API docs at http://localhost:8000/docs (dev only). Demo-day steps: [docs/RUNBOOK.md](docs/RUNBOOK.md).
