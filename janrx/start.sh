#!/usr/bin/env bash
# One-command run.  ./start.sh          -> Docker (recommended)
#                   ./start.sh --local  -> local venv, no Docker
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example (OCR_PROVIDER=mock, so the demo works without a model)."
fi

if [ "${1:-}" = "--local" ]; then
  cd backend
  [ -d .venv ] || python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -q -r requirements.txt
  set -a; source ../.env; set +a
  export DATA_DIR="../${DATA_DIR:-data}"
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
  exec docker compose up --build
fi
