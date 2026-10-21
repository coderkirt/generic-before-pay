#!/usr/bin/env python3
"""
validate_and_normalize.py

Validates and normalizes curated drug datasets (JSON/CSV) for Generic Before Pay.
Enforces safety rules:
- Prohibits dosage, frequency, and substitution-advice fields.
- Validates required fields: id, brand_name, molecule, strength, branded_price, generic_price, source.
- Standardizes strength formatting and computes savings.
- Generates a deterministic SHA256 content hash for offline bundle sync.
"""

import sys
import json
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

FORBIDDEN_FIELDS = {
    "dosage",
    "dosage_instructions",
    "frequency",
    "duration",
    "course",
    "substitution_advice",
    "recommendation",
    "recommendation_level",
    "advice",
}

REQUIRED_FIELDS = {
    "id": str,
    "brand_name": str,
    "molecule": str,
    "strength": str,
    "unit": str,
    "branded_price": (int, float),
    "generic_price": (int, float),
    "source": str,
}


def normalize_strength(strength: str) -> str:
    """Normalize strength strings (e.g. '500mg' -> '500 mg')."""
    s = re.sub(r'(\d+)\s*(mg|ml|mcg|gm|g|iu|%)\b', r'\1 \2', strength, flags=re.IGNORECASE)
    # clean extra whitespace around '+'
    s = re.sub(r'\s*\+\s*', ' + ', s)
    return s.strip()


def validate_and_normalize_record(record: Dict[str, Any], index: int) -> Tuple[Dict[str, Any], List[str]]:
    errors = []
    
    # 1. Check for forbidden fields
    found_forbidden = [f for f in record.keys() if f.lower() in FORBIDDEN_FIELDS]
    if found_forbidden:
        errors.append(f"Record #{index} contains forbidden medical advice/dosage fields: {found_forbidden}")

    # 2. Check required fields and types
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in record:
            errors.append(f"Record #{index} missing required field '{field}'")
        elif not isinstance(record[field], expected_type):
            errors.append(
                f"Record #{index} field '{field}' has invalid type {type(record[field]).__name__}, "
                f"expected {expected_type}"
            )

    if errors:
        return record, errors

    # 3. Value validations
    brand_name = record["brand_name"].strip()
    molecule = record["molecule"].strip()
    strength = normalize_strength(record["strength"])
    unit = record["unit"].strip()
    branded_price = round(float(record["branded_price"]), 2)
    generic_price = round(float(record["generic_price"]), 2)
    source = record["source"].strip()

    if not brand_name:
        errors.append(f"Record #{index} has empty brand_name")
    if not molecule:
        errors.append(f"Record #{index} has empty molecule")
    if branded_price < 0 or generic_price < 0:
        errors.append(f"Record #{index} prices cannot be negative")

    # 4. Computed savings
    savings_amount = max(0.0, round(branded_price - generic_price, 2))
    savings_pct = round((savings_amount / branded_price) * 100, 1) if branded_price > 0 else 0.0

    normalized_record = {
        "id": record.get("id") or re.sub(r'[^a-z0-9]+', '-', f"{brand_name}-{strength}".lower()).strip('-'),
        "brand_name": brand_name,
        "molecule": molecule,
        "strength": strength,
        "unit": unit,
        "branded_price": branded_price,
        "generic_price": generic_price,
        "savings_amount": savings_amount,
        "savings_percentage": savings_pct,
        "source": source,
        "aliases": [a.strip().lower() for a in record.get("aliases", []) if a.strip()],
    }

    return normalized_record, errors


def process_dataset(input_path: Path) -> Tuple[List[Dict[str, Any]], str, List[str]]:
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        return [], "", [f"Dataset root must be a list of records, got {type(data).__name__}"]

    all_errors = []
    normalized_records = []
    seen_ids = set()

    for idx, item in enumerate(data):
        norm_item, item_errors = validate_and_normalize_record(item, idx + 1)
        all_errors.extend(item_errors)
        if not item_errors:
            item_id = norm_item["id"]
            if item_id in seen_ids:
                all_errors.append(f"Duplicate id '{item_id}' found at record #{idx + 1}")
            seen_ids.add(item_id)
            normalized_records.append(norm_item)

    # Compute deterministic SHA256 of normalized records
    canonical_json = json.dumps(normalized_records, sort_keys=True, separators=(',', ':')).encode('utf-8')
    dataset_hash = hashlib.sha256(canonical_json).hexdigest()

    return normalized_records, dataset_hash, all_errors


def main():
    base_dir = Path(__file__).resolve().parent.parent
    input_file = base_dir / "data" / "curated_drugs.json"
    
    if not input_file.exists():
        print(f"Error: {input_file} not found.")
        sys.exit(1)

    print(f"Validating dataset: {input_file}")
    records, dataset_hash, errors = process_dataset(input_file)

    if errors:
        print(f"\n[FAILED] Validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    print(f"[PASSED] Successfully validated {len(records)} records.")
    print(f"Dataset SHA256 Hash: {dataset_hash}")

    # Write back the normalized version to data/curated_drugs.json
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Formatted and saved normalized data to {input_file}")


if __name__ == "__main__":
    main()
