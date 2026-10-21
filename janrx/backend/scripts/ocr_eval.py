"""Send printed-box photos to POST /v1/ocr and write a measurement report.

Does not interpret drug facts. Review the JSON by hand and fill evals/boxes/README.md.
Never commit prescription photos that identify a patient.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import httpx

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://localhost:8000")
    p.add_argument("--images", type=Path, default=Path("evals/boxes"))
    p.add_argument("--out", type=Path, default=Path("evals/report.json"))
    p.add_argument("--language", default="en")
    args = p.parse_args()

    files = sorted(f for f in args.images.iterdir() if f.suffix.lower() in IMAGE_SUFFIXES) if args.images.is_dir() else []
    if not files:
        raise SystemExit(f"No images in {args.images}. See evals/boxes/README.md")

    rows = []
    with httpx.Client(timeout=60.0) as client:
        for path in files:
            with path.open("rb") as fh:
                resp = client.post(
                    f"{args.base_url.rstrip('/')}/v1/ocr",
                    files={"file": (path.name, fh, "application/octet-stream")},
                    data={"language": args.language},
                )
            body = resp.json()
            error = body.get("error") or {}
            rows.append({
                "file": path.name,
                "http_status": resp.status_code,
                "error_code": error.get("code"),
                "fallback": error.get("fallback"),
                "mock": body.get("mock"),
                "provider": body.get("provider"),
                "candidate_count": len(body.get("candidates") or []),
                "text_chars": len(body.get("text") or ""),
                # text/candidates omitted so the report is safer to share
            })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"base_url": args.base_url, "n": len(rows), "results": rows}, indent=2), encoding="utf-8")
    print(f"Wrote {args.out} ({len(rows)} images)")


if __name__ == "__main__":
    main()
