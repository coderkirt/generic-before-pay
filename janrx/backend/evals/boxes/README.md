# Printed-box OCR eval (BE-2)

Put **at least 10** photos of printed medicine boxes, strips, or printed prescriptions here. No handwritten pads as the promised set. No patient name, address, or face in frame.

Then, with the API running (`OCR_PROVIDER=gemma`):

```bash
cd backend
python scripts/ocr_eval.py --base-url http://localhost:8000 --images evals/boxes
```

Fill this table by hand. Do not guess. Handwriting is unsupported even if a photo sneaks in.

| # | File | Printed? | Candidates usable? | Notes / known failures |
| --- | --- | --- | --- | --- |
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |
| 9 | | | | |
| 10 | | | | |

Hardware, Ollama version, `GEMMA_MODEL`, and p50/p95 latency go in `backend/README.md` after this run.
