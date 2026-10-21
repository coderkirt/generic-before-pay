# Data folder

Put the curated, source-cited datasets here (see docs/PRD.md section 8):

- `brands.json`
- `janaushadhi_products.json`
- `kendras.json`

These are intentionally NOT included. Do not invent prices or drug facts. Every row needs `source` and `price_date`.
Until files exist, the data-backed endpoints return `503 DATA_NOT_LOADED` (this is the honest behaviour).
Tests use synthetic fixtures in `backend/tests/fixtures/`, which are fake and must never be shipped as real data.
