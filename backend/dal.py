"""
backend/dal.py

Data Access Layer (DAL) for Generic Before Pay.
Provides safe, read-only queries for drug search, detail, compare, and data bundles.
Strictly guarantees no medical dosage or frequency advice is provided.
"""

import json
import sqlite3
from typing import Dict, Any, List, Optional
from backend.database import get_db_connection

STANDARD_DISCLAIMER = (
    "This shows published generic names and indicative prices for medicines already named. "
    "It is not medical advice and it is not a recommendation to substitute. "
    "Confirm the medicine, the strength, and the price with your doctor or pharmacist "
    "before you buy or change anything."
)


def _row_to_drug_dict(row: sqlite3.Row) -> Dict[str, Any]:
    branded_price = float(row["branded_price"])
    generic_price = float(row["generic_price"])
    savings_amount = max(0.0, round(branded_price - generic_price, 2))
    savings_pct = round((savings_amount / branded_price) * 100, 1) if branded_price > 0 else 0.0

    aliases = []
    try:
        aliases = json.loads(row["aliases"])
    except Exception:
        aliases = []

    return {
        "id": row["id"],
        "brand_name": row["brand_name"],
        "molecule": row["molecule"],
        "strength": row["strength"],
        "unit": row["unit"],
        "branded_price": branded_price,
        "generic_price": generic_price,
        "savings_amount": savings_amount,
        "savings_percentage": savings_pct,
        "source": row["source"],
        "aliases": aliases
    }


def get_drug_by_id(drug_id: str, conn: Optional[sqlite3.Connection] = None) -> Optional[Dict[str, Any]]:
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM drugs WHERE id = ?", (drug_id,))
        row = cur.fetchone()
        if not row:
            return None
        return _row_to_drug_dict(row)
    finally:
        if should_close:
            conn.close()


def get_all_drugs(conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM drugs ORDER BY brand_name ASC")
        rows = cur.fetchall()
        return [_row_to_drug_dict(r) for r in rows]
    finally:
        if should_close:
            conn.close()


def search_drugs(query: str, limit: int = 3, conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
    """
    Search drugs via the Data Access Layer, querying SQLite as the single source of truth.
    """
    from backend.search import fuzzy_search_drugs
    drugs = get_all_drugs(conn=conn)
    return fuzzy_search_drugs(query=query, drugs=drugs, limit=limit)


def get_dataset_metadata(conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
    """
    Fetches dataset version, hash, and record count directly from SQLite metadata.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True

    try:
        cur = conn.cursor()
        cur.execute("SELECT key, value FROM dataset_metadata")
        rows = cur.fetchall()
        meta = {r["key"]: r["value"] for r in rows}
        cur.execute("SELECT COUNT(*) FROM drugs")
        meta["total_records"] = cur.fetchone()[0]
        return meta
    finally:
        if should_close:
            conn.close()


def calculate_compare(items: List[Dict[str, Any]], conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
    """
    Given a list of items `[{"id": "...", "quantity": int}, ...]`,
    calculates per-item savings and aggregated prescription savings.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True

    try:
        breakdown = []
        total_branded_cost = 0.0
        total_generic_cost = 0.0
        total_units = 0

        for item in items:
            drug_id = item.get("id")
            quantity = max(1, int(item.get("quantity", 1)))
            drug = get_drug_by_id(drug_id, conn=conn)

            if not drug:
                continue

            b_total = round(drug["branded_price"] * quantity, 2)
            g_total = round(drug["generic_price"] * quantity, 2)
            item_savings = max(0.0, round(b_total - g_total, 2))
            item_pct = round((item_savings / b_total) * 100, 1) if b_total > 0 else 0.0

            total_branded_cost += b_total
            total_generic_cost += g_total
            total_units += quantity

            breakdown.append({
                "id": drug["id"],
                "brand_name": drug["brand_name"],
                "molecule": drug["molecule"],
                "strength": drug["strength"],
                "unit": drug["unit"],
                "quantity": quantity,
                "branded_unit_price": drug["branded_price"],
                "generic_unit_price": drug["generic_price"],
                "branded_total_price": b_total,
                "generic_total_price": g_total,
                "item_savings": item_savings,
                "savings_percentage": item_pct
            })

        total_branded_cost = round(total_branded_cost, 2)
        total_generic_cost = round(total_generic_cost, 2)
        total_savings = max(0.0, round(total_branded_cost - total_generic_cost, 2))
        overall_pct = (
            round((total_savings / total_branded_cost) * 100, 1)
            if total_branded_cost > 0
            else 0.0
        )

        return {
            "summary": {
                "total_items": len(breakdown),
                "total_units": total_units,
                "total_branded_cost": total_branded_cost,
                "total_generic_cost": total_generic_cost,
                "total_savings": total_savings,
                "overall_savings_percentage": overall_pct,
                "currency": "INR"
            },
            "breakdown": breakdown,
            "disclaimer": STANDARD_DISCLAIMER
        }
    finally:
        if should_close:
            conn.close()
