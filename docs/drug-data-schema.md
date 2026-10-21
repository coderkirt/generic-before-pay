# Generic Before Pay — Drug Data Schema

This document defines the core data model and safety constraints for drug records in Generic Before Pay.

---

## 1. Safety & Regulatory Constraints (Non-Negotiable)

1. **Information, Not Advice**: This platform provides pricing and molecule comparison between branded medicines and generic alternatives (e.g. Jan Aushadhi). It **never** provides medical diagnosis, prescription advice, or automated substitution recommendations.
2. **Strict Field Blacklist**: The schema **MUST NOT** include:
   - `dosage` or `dosage_instructions`
   - `frequency` (e.g. "twice daily", "after meals")
   - `duration` or `course`
   - `substitution_advice` or `recommendation_level`
   - `prescription_required` flags interpreted as advice
3. **Mandatory Disclaimer**: Every response serving drug data must include the verbatim disclaimer:
   > *"This shows published generic names and indicative prices for medicines already named. It is not medical advice and it is not a recommendation to substitute. Confirm the medicine, the strength, and the price with your doctor or pharmacist before you buy or change anything."*

---

## 2. Core Schema Definition

Each drug record represents a specific branded or generic presentation mapped to its active molecule and generic equivalent price.

| Field Name | Type | Constraints | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `String` (UUID / slug) | Unique, Primary Key, alphanumeric + hyphen | Stable unique identifier for the drug record | `"paracetamol-500mg-tab"` |
| `brand_name` | `String` | Required, 1-120 chars, trimmed | Commercial or trade name of the branded formulation | `"Calpol 500"`, `"Dolo 650"` |
| `molecule` | `String` | Required, 1-200 chars, normalized | Active Pharmaceutical Ingredient (API) / generic salt formulation | `"Paracetamol"`, `"Metformin Hydrochloride"` |
| `strength` | `String` | Required, 1-50 chars, normalized format | Strength / concentration per unit dose | `"500 mg"`, `"650 mg"`, `"500 mg + 5 mg"` |
| `unit` | `String` | Required, e.g., `"strip of 10 tablets"`, `"100 ml bottle"` | Packaging unit for which the prices apply | `"strip of 10 tablets"` |
| `branded_price` | `Float` | Required, `>= 0.00`, 2 decimal places | Indicative or MRP price of the branded drug in INR (₹) | `32.50` |
| `generic_price` | `Float` | Required, `>= 0.00`, 2 decimal places | Indicative price of the generic equivalent (Jan Aushadhi / PMBJP) in INR (₹) | `5.00` |
| `source` | `String` | Required, authoritative reference | Source and version of the pricing data | `"PMBJP Price List Sep 2024 / NPPA"` |
| `aliases` | `Array[String]` | Optional, alternative spellings / transliterations | Common misspellings or regional phonetic aliases | `["kalpol", "crocin", "paracip"]` |

---

## 3. Derived / Computed Attributes (API Layer)

These fields are calculated dynamically and **not stored as static values**:

- **`savings_amount`**: `max(0.00, branded_price - generic_price)`
- **`savings_percentage`**: `round(((branded_price - generic_price) / branded_price) * 100, 1)` if `branded_price > 0` else `0.0`

---

## 4. Normalization Rules

1. **Whitespace**: Trim leading/trailing whitespace, collapse multiple internal spaces to a single space.
2. **Letter Casing**:
   - `brand_name`: Title Case or original brand capitalisation (e.g., `"Calpol"`).
   - `molecule`: Normalized Title Case with standard chemical conventions (e.g., `"Metformin Hydrochloride"`).
   - Search indexing tokens: Lowercase ASCII fold (e.g., `"calpol 500"`, `"paracetamol 500 mg"`).
3. **Strength formatting**:
   - Always standardise with space between number and unit: `"500mg"` → `"500 mg"`, `"10ml"` → `"10 ml"`.
   - Multi-drug combinations separated by `+`: `"500 mg + 50 mg"`.
4. **Currency**:
   - Rounded to 2 decimal places, denominated in Indian Rupee (INR ₹).
   - Values must be strictly non-negative.
