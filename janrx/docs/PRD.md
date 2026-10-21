# PRD: Prescription Price Clarity (working title: "JanRx")

> **For Cursor:** Read this whole document before writing code. Section 12 lists the build order. Section 4 lists non-negotiable safety rules that override any convenience.

---

## 1. Overview

**One-line:** A patient scans or types a prescription and instantly sees what each branded medicine costs versus its Jan Aushadhi generic with the same composition, plus plain information about each medicine and the nearest Jan Aushadhi Kendra.

**Headline output:** `₹240 → ₹28` per medicine, and a total saving for the whole prescription.

**Problem:** Patients receive prescriptions with brand names they cannot read or understand, and pay whatever the chemist quotes. For many drugs an identical-composition generic exists at a fraction of the price at Jan Aushadhi Kendras (PMBJP). The patient has no way to know this.

**Product principle:** Make cost visible before payment. Never make a medical decision for the patient.

## 2. Goals

1. Show the price gap (brand vs Jan Aushadhi generic) as the first and biggest thing on screen.
2. Let the user scan or upload a prescription and extract the prescribed medicines.
3. Require manual patient age and gender entry, used to confirm the prescription context.
4. Compare prices by **composition** (molecule + strength + dosage form).
5. Show basic, curated information about each medicine (what it is generally used for).
6. Handle misspellings gracefully, with honest, non-overconfident results.
7. Show the nearest Jan Aushadhi Kendra to the user.
8. Always carry a real disclaimer: information only, not medical advice.

### Non-goals
- No recommendation or instruction to substitute, stop, start, or change any medicine.
- No dosage recommendations, no diagnosis, no drug interaction advice.
- No ordering, payments, or delivery.
- No reading of messy handwriting as a promised capability (best effort only, always user-confirmed).

## 3. Target users
- Patients and caregivers in India, often price-sensitive, often low literacy in English.
- Secondary: pharmacists, health workers, and NGO volunteers helping patients.
- Design for a low-end Android phone on a slow connection.

## 4. Safety and honesty rules (non-negotiable)

1. **No LLM-generated drug information.** Every medicine fact (composition, strength, price, usage) must come from the bundled dataset. If it is not in the data, display: *"Not in our data. Please ask your pharmacist or doctor."*
2. **No substitution advice.** Wording must be "A Jan Aushadhi product with the same listed composition is priced at ₹X." Never "you should switch" or "safe to replace."
3. **Disclaimer is always visible** on the results screen and in every printout (see 9.1).
4. **Never claim certainty on fuzzy matches** (see 6.3).
5. **Age/gender are used for confirmation display and for showing label-based notes from the dataset only.** The app never computes or suggests a dose.
6. **Prices are indicative.** Show source and "last updated" date next to every price.
7. **Privacy:** prescription images are processed and discarded; not uploaded to a server for storage; no accounts required. Location is used only in-session.

## 5. Feature specification

### F1. Prescription scan and extraction
- Input: camera capture or image upload (JPG/PNG). Also a typed/manual entry path that **always works**.
- Pipeline: image → preprocessing (deskew, contrast) → OCR → candidate medicine lines → match each to dataset (F4).
- Scope: printed prescriptions, strips, and boxes are supported. Handwriting is best-effort; show a banner: *"Handwriting may be read incorrectly. Please check each item."*
- Output: an editable list of detected medicines. The user can fix, delete, or add items before results are generated.
- Each detected line shows the raw OCR text next to the matched medicine so the user can verify.
- Tech: calls the backend `POST /v1/ocr` (Gemma vision model used as a text reader only; section 15). Optional on-device Tesseract.js fallback. OCR text is only used to *find candidates in the dataset*, never to generate drug facts.

### F2. Patient confirmation (age and gender)
- Required fields before results: **age** (years, or months for infants) and **gender** (Male / Female / Other / Prefer not to say).
- Purpose: let the user confirm the prescription belongs to the right person, and display dataset-based notes (for example, a label note such as "pediatric formulation" or "adult strength" if present in the data).
- If a matched product's dataset record has an age-group tag that does not fit the entered age, show a neutral flag: *"This product's listing is for adults. Please confirm with your doctor or pharmacist."* Do not state it is wrong or unsafe.
- Confirmation step: "Is this prescription for a [age]-year-old [gender]? ✔ Yes / ✎ Edit".

### F3. Price comparison by composition
- Match key: **molecule(s) + strength + dosage form** (tablet, capsule, syrup, injection, etc.).
- For each medicine show:
  - Prescribed brand: name, manufacturer, pack size, indicative MRP.
  - Jan Aushadhi equivalent(s): generic name, strength, pack size, price.
  - **Saving per pack and percentage**, normalised per unit (per tablet / per ml) when pack sizes differ.
- Headline card format: large `₹240 → ₹28`, "You could pay ₹212 less" subtext.
- Prescription summary: total brand cost, total Jan Aushadhi cost, **total saving**.
- Partial and mismatch handling:
  - Composition matches but strength differs → show as "Different strength listed" and do not include in the saving total.
  - Combination drugs → match only if every component and strength matches exactly.
  - No Jan Aushadhi equivalent → show "No Jan Aushadhi product with this composition in our data" and exclude from the total.
- Show NPPA ceiling price where available as a reference line.

### F4. Fuzzy matching with calibrated confidence
- Match against brand names, molecule names, and common aliases.
- Techniques to combine: normalisation (lowercase, strip punctuation, strip strength tokens), character n-gram similarity, Damerau-Levenshtein distance, phonetic matching (Double Metaphone), and a small Indian-brand alias list.
- Parse strength from input if present ("Pantocid 40" → 40 mg); if missing, show all dataset strengths for that molecule and ask the user to pick.
- Return a score and map it to tiers:

| Tier | Condition | UI behaviour |
|---|---|---|
| Exact | Normalised exact match | Show result normally |
| Likely | High score, clear winner | Show result with banner: *"We matched this to **X**. The spelling you entered was different. Please check it against your prescription."* |
| Uncertain | Medium score or close runner-up | Show "Did you mean…?" with up to 3 options. No price shown until user picks |
| No match | Low score | *"Not in our data."* Offer manual edit. Never guess |

- Misspelled matches always display a visible "Please verify" marker and never use confident wording like "Correct" or "Confirmed".
- Include a test file of at least 50 misspelling cases (for example `Crosin`, `Pantocid40`, `Azithral`, `metformine`, `Dolo650`) with expected outcomes, and run it in CI.

### F5. Medicine information (basic, curated)
- For each matched medicine show, **from the dataset only**:
  - Active composition and strength
  - Drug class (for example "Antacid / proton pump inhibitor")
  - **Common general uses** in plain language, 1 to 2 lines (for example "Commonly used for acid reflux and stomach ulcers")
  - Dosage form
  - Label-level notes if present (for example "Take on empty stomach" only if sourced)
- Every info block carries: *"General information from [source]. Your doctor decides why this was prescribed for you."*
- Do **not** show dosage amounts, duration, side-effect lists, or interaction claims unless sourced from a vetted dataset field with a citation. Default for v1: omit them.
- Content must be reviewed by a human before shipping; mark each record with `reviewed_by` and `reviewed_on`.
- Support English and Hindi for uses text (static, pre-translated and human-checked, not runtime LLM translation).

### F6. Nearest Jan Aushadhi Kendra
- Ask for browser geolocation permission. Fallback: enter PIN code or city/district.
- Use a **bundled** dataset of Kendras (name, address, PIN, district, state, lat/lng, phone if available) so it works offline.
- Compute distance with the haversine formula; show the 3 nearest with distance, address, and an "Open in Maps" link (a deep link, not an embedded dependency).
- Show data freshness date and a note: *"Please call ahead; stock may vary."*
- Optional enhancement: live lookup from the official store locator when online, falling back to the bundled list.

### F7. Printable sheet (high value, low effort)
- One-page printable/PDF "counter sheet": patient age and gender, medicine table (brand, composition, Jan Aushadhi equivalent, both prices), total saving, nearest Kendra, disclaimer in English and Hindi.
- Wording on the sheet: "Please show this to your doctor or pharmacist" and "Ask if a Jan Aushadhi equivalent is suitable for me."

## 6. Additional features recommended (from earlier discussion and product thinking)

**Include in v1 if time allows**
1. **Printable counter sheet** (F7). Helps the patient act without arguing at the counter.
2. **"Ask your doctor" prompt list**: auto-generated neutral questions such as "Is a generic with the same composition suitable for me?" Not advice, only a conversation aid.
3. **Hindi interface** and optional **voice input** for drug names (Web Speech API) for low-literacy users.
4. **Per-unit pricing** so different pack sizes compare fairly.
5. **Data provenance and freshness** shown on every price (source, date).
6. **Honest empty states** for unknown drugs, with a "Report a missing medicine" button (stores locally or sends to a form, no personal data).
7. **Offline-first PWA** so the demo and low-connectivity use both work.

**Later (v2)**
8. Pill identifier by imprint (needs a vetted imprint dataset).
9. Share results via WhatsApp (text summary and sheet link).
10. Savings tracker over time (local only).
11. Pharmacist mode: faster batch entry, QR code that opens the same result.
12. Refill and cost reminders. Add only with careful privacy design.
13. State-wise price and Kendra coverage analytics for NGOs (aggregate, anonymised).

**Explicitly avoid:** symptom checkers, "AI doctor" chat, dosage calculators, interaction checkers without a licensed dataset.

## 7. User flow

1. **Landing:** headline value, disclaimer summary, buttons: *Scan prescription* / *Type medicine names*.
2. **Capture or upload** image (or manual entry).
3. **Review extracted medicines:** edit raw text, fix matches, add or remove items.
4. **Enter patient details:** age and gender; confirm.
5. **Results:** total saving banner, then per-medicine cards (price comparison first, info collapsed below).
6. **Nearest Kendra:** location permission or PIN entry.
7. **Print / save sheet.**

Fuzzy "Did you mean" resolution happens inline at step 3.

## 8. Data requirements

Bundled as JSON or CSV in the repo. No runtime dependency on external sites for core flows.

**Scope:** curate roughly 200 to 300 common drugs well rather than scraping thousands badly.

### 8.1 `medicines.json` (generic compositions)
```json
{
  "composition_id": "pantoprazole_40_tablet",
  "molecules": [{ "name": "Pantoprazole", "strength": "40", "unit": "mg" }],
  "dosage_form": "tablet",
  "drug_class": "Proton pump inhibitor",
  "common_uses_en": "Commonly used for acid reflux and stomach ulcers.",
  "common_uses_hi": "...",
  "age_group_note": "adult",
  "info_source": "…",
  "reviewed_by": "…",
  "reviewed_on": "2026-10-01"
}
```

### 8.2 `brands.json`
```json
{
  "brand_id": "pantocid_40_tab_15",
  "brand_name": "Pantocid",
  "aliases": ["pantocid", "pantocid 40"],
  "manufacturer": "Sun Pharma",
  "composition_id": "pantoprazole_40_tablet",
  "pack_size": 15,
  "pack_unit": "tablets",
  "mrp_inr": 190.0,
  "mrp_source": "NPPA ceiling / label",
  "price_date": "2026-09-01"
}
```

### 8.3 `janaushadhi_products.json`
```json
{
  "ja_code": "…",
  "generic_name": "Pantoprazole Gastro-resistant Tablets IP 40 mg",
  "composition_id": "pantoprazole_40_tablet",
  "pack_size": 10,
  "pack_unit": "tablets",
  "price_inr": 14.0,
  "source": "PMBJP product list",
  "price_date": "2026-09-01"
}
```

### 8.4 `kendras.json`
```json
{ "kendra_code": "…", "name": "…", "address": "…", "pincode": "…", "district": "…", "state": "…", "lat": 26.85, "lng": 80.94, "phone": "…", "data_date": "2026-09-01" }
```

### 8.5 Data sources
- Jan Aushadhi (PMBJP / BPPI) product list and prices
- NPPA ceiling prices (DPCO / NLEM)
- PMBJP Kendra locator list
- Brand MRPs from NPPA schedules, official labels, or other citeable public data
- Record the source and date for every row. Validate with a script that fails the build on missing fields.

## 9. UX requirements

### 9.1 Disclaimer (exact intent; final copy to be reviewed)
> **This is price and composition information only. It is not medical advice.** Prices are indicative and may differ. We do not recommend changing any medicine. Always confirm with your doctor or pharmacist before making any decision.

Shown: footer of every results screen, on the saving banner (short form), and on every printout.

### 9.2 Design
- Mobile-first, large tap targets, high contrast, minimum 16px body text.
- Saving figure is the largest element on each card.
- Colour is never the only signal (accessibility).
- Plain language; avoid jargon. English and Hindi toggle on every screen.
- Loading and error states for OCR, geolocation denied, and no internet.

## 10. Technical recommendations

- **Frontend:** Next.js (App Router) + TypeScript + Tailwind, PWA with service worker for offline.
- **Matching engine:** pure TypeScript module in `/lib/matching`, with no network calls, fully unit-tested.
- **Data:** static JSON loaded client-side (or a lightweight SQLite/IndexedDB layer if the dataset grows).
- **OCR:** primary path is the backend Gemma OCR endpoint (section 15). Optional on-device Tesseract.js fallback behind an `OcrProvider` interface. Typed entry always works.
- **Geolocation:** browser Geolocation API + haversine on bundled Kendra data.
- **Printing:** CSS print stylesheet, or `@react-pdf/renderer` for the sheet.
- **i18n:** `next-intl` or similar, with static translation files.
- **Backend:** FastAPI (Python 3.12) in `/backend`, Docker one-command run (section 15).
- **Testing:** Vitest for matching and price logic; Playwright for the main flow.

Suggested structure:
```
/app            routes (scan, review, results, kendras, print)
/components     SavingCard, MedicineCard, DisclaimerBanner, DidYouMean, KendraList
/lib/matching   normalise.ts, fuzzy.ts, strength.ts, tiers.ts
/lib/pricing    compare.ts (per-unit math, totals)
/lib/kendra     nearest.ts
/lib/ocr        provider.ts, tesseract.ts, parseLines.ts
/data           medicines.json, brands.json, janaushadhi_products.json, kendras.json
/scripts        validate-data.ts, build-index.ts
/tests          misspellings.json, matching.test.ts, pricing.test.ts
```

## 11. Acceptance criteria

1. Typing `Crosin`, `Pantocid40`, or `metformine` returns the correct medicine with a "please verify" marker, not a confident statement.
2. A very low-confidence input shows "Not in our data" and **never** a guessed price.
3. The saving (`₹X → ₹Y`) is the most prominent element on every medicine card; a total saving is shown for multi-item prescriptions.
4. Prices are compared by composition (molecule, strength, form) and normalised per unit.
5. Age and gender are required before results display; a confirmation step exists.
6. Medicine info appears only for records present in the dataset; none is generated at runtime.
7. The nearest 3 Kendras are shown using geolocation or PIN fallback, and work offline from bundled data.
8. The disclaimer is visible on results and on the printed sheet; no screen uses substitution-recommending language.
9. The typed-entry path works end to end with no OCR and no internet.
10. The data validator passes (all rows have source and date).
11. The 50+ case misspelling suite passes at an agreed threshold (for example 90% correct tier assignment, 0 confident wrong matches).

## 12. Build order for Cursor

1. Scaffold project, data schemas, and the validation script; load a seed set of 30 medicines.
2. Matching engine with tiers and the misspelling test suite.
3. Price comparison logic (per-unit, totals, mismatch handling).
4. Typed-entry UI: results with saving headline, disclaimer, "Did you mean".
5. Age and gender confirmation step.
6. Medicine info panel from dataset.
7. Kendra finder (geolocation + PIN fallback).
8. Printable sheet.
9. OCR scan flow with the review and edit screen.
10. Hindi, voice input, PWA offline, polish.
11. Expand dataset toward 200+ medicines with human review.

## 13. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Wrong match leads to wrong price shown | Tiered confidence, "please verify," no price on uncertain matches |
| User reads results as medical advice | Neutral wording, persistent disclaimer, no substitution language |
| Outdated prices | Source and date on every price, data freshness warnings |
| OCR errors on handwriting | Printed-first scope, mandatory review screen, typed path always available |
| Incorrect medicine uses text | Curated, human-reviewed, sourced data only; no runtime generation |
| Kendra data stale or missing | Bundled data with date, "call ahead" note, PIN fallback |
| Privacy of prescription photos | On-device processing, no storage, no accounts |

## 14. Open questions
- Which licensed or public source will supply brand MRPs and verified "common uses" text?
- Who is the human reviewer for medicine information before release?
- Is the age-group note available per product in the sources, or must it be curated manually?
- Which languages beyond English and Hindi are needed?


---

## 15. Backend: AI/OCR, Security and Ops (Backend Member 2)

**Role of the model:** read printed text from medicine boxes, strips, and printed prescriptions. Nothing else. It never produces dosage, drug facts, uses, warnings, or substitution advice. All facts come from shipped data.

### 15.1 Core requirements
| # | Requirement | Acceptance |
|---|---|---|
| B1 | FastAPI skeleton (`create_app` factory) | App starts; `/docs` in dev only |
| B2 | Health and readiness: `GET /healthz`, `GET /readyz` | `/readyz` is 200 even if OCR is down, with `status: degraded` and `typing_path: available` |
| B3 | Gemma OCR endpoint `POST /v1/ocr` for printed boxes/strips | Returns `text` + `candidates` only |
| B4 | Output guard | Candidates must literally appear in extracted text; short plain names only; no other fields leave the OCR layer |
| B5 | Clear fallback | Model down/slow/bad output returns 503/504/502 with `fallback: "manual_entry"`; typing endpoints unaffected |
| B6 | Upload limits and timeouts | Content-Length pre-check, streamed size cap (default 5 MB), magic-byte and Pillow validation, pixel cap, request timeout (default 20 s) |
| B7 | CORS for the PWA | Exact-origin allow-list via `CORS_ORIGINS`; wildcard rejected in prod |
| B8 | Rate limiting on OCR | Default 10 per minute per client; 429 with `Retry-After` |
| B9 | Request IDs and structured logs | `X-Request-ID` on every response; JSON logs; no images, extracted text, or patient age/gender logged |
| B10 | Disclaimer on every OCR-related response | Present on success and on every error envelope |
| B11 | Dockerfile and one-command start | `./start.sh` runs everything; non-root container |
| B12 | `.env.example`, no secrets in repo | `.env` gitignored |
| B13 | Mocked tests | OCR success, failure, timeout, bad output, fallback, limits, rate limit, CORS |
| B14 | README documents model, runtime, prompt/job, limitations, credits | See `backend/README.md` |

### 15.2 Optional requirements
| # | Requirement | Notes |
|---|---|---|
| O1 | Prescription aggregation | `POST /v1/prescription/candidates` (fuzzy candidates, no prices) and `POST /v1/prescription/summary` (totals; requires `confirmed_by_user: true`; only fully comparable lines count) |
| O2 | Nearest Kendra | `GET /v1/kendras/nearest` returns nearest 3 with distance and maps link, from bundled data |
| O3 | Image pre-processing | Orientation fix, grayscale, autocontrast, downscale, light sharpen |
| O4 | Language hint | `language` form field (for example `en`, `hi`), echoed in response |
| O5 | Basic API metrics | `GET /v1/metrics` in-memory counters, no personal data |
| O6 | Mock mode | `OCR_PROVIDER=mock` returns fixed output flagged `mock: true` so the demo works without a model |

### 15.3 API summary
Full contract in `docs/API.md`. All error responses share one envelope: `request_id`, `error{code,message,fallback}`, `disclaimer`.

### 15.4 Frontend integration rules
1. Treat `candidates` as unverified text. Run them through the fuzzy matcher and require user confirmation (review screen).
2. On any 5xx/429 from `/v1/ocr`, show the error message and move the user to typed entry. Never block the flow.
3. If `mock: true`, show a visible "Demo mode" badge.
4. Show the `disclaimer` from OCR/prescription responses.

### 15.5 Backend risks
| Risk | Mitigation |
|---|---|
| Model invents drug facts | Prompt forbids it; output reduced to `text` + sanitised `candidates`; no other fields returned |
| Model unavailable on demo day | Mock mode; typing always works; `/readyz` shows degraded state |
| Oversized or malicious uploads | Size, type, pixel limits; timeouts; rate limit |
| Privacy | Images processed in memory only; logs hold no images, text, or patient details |
| Gemma runtime/licence unknown | Open question below |

### 15.6 Open questions (backend)
- Which exact Gemma model id and runtime will be used, and what hardware will the demo run on? Record in `backend/README.md` once measured.
- Will the rate limiter need Redis (multiple instances)?
- Who owns producing and validating the `/data` files that `/v1/prescription/*` and `/v1/kendras/*` depend on?

---

## 16. Repository layout for Cursor
```
AGENTS.md               read first (hard safety rules)
.cursor/rules/*.mdc     project, safety, backend rules
docs/PRD.md  TASKS.md  API.md
backend/                FastAPI service + tests (Python 3.12)
data/                   curated datasets (to be added, with sources)
web/                    PWA frontend (frontend teammate)
.env.example  docker-compose.yml  start.sh
```
Cursor workflow: read `AGENTS.md`, then work through `docs/TASKS.md` top to bottom, keep `pytest` green, and tick tasks as they complete.
