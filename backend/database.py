"""
backend/database.py

SQLite Database initialization and seeding for Generic Before Pay.
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "drugs.db"
DEFAULT_SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "curated_drugs.json"


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    target_path = db_path or DEFAULT_DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None, seed_path: Optional[Path] = None, force_reload: bool = False) -> None:
    conn = get_db_connection(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS drugs (
            id TEXT PRIMARY KEY,
            brand_name TEXT NOT NULL,
            molecule TEXT NOT NULL,
            strength TEXT NOT NULL,
            unit TEXT NOT NULL,
            branded_price REAL NOT NULL,
            generic_price REAL NOT NULL,
            source TEXT NOT NULL,
            aliases TEXT NOT NULL,
            brand_name_lower TEXT NOT NULL,
            molecule_lower TEXT NOT NULL
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_brand_name_lower ON drugs(brand_name_lower)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_molecule_lower ON drugs(molecule_lower)")
    conn.commit()

    if force_reload:
        cur.execute("DELETE FROM drugs")
        conn.commit()

    # Check if empty, then seed
    cur.execute("SELECT COUNT(*) FROM drugs")
    count = cur.fetchone()[0]

    if count == 0:
        actual_seed_path = seed_path or DEFAULT_SEED_PATH
        if actual_seed_path.exists():
            with open(actual_seed_path, "r", encoding="utf-8") as f:
                records = json.load(f)

            for item in records:
                cur.execute("""
                    INSERT OR REPLACE INTO drugs (
                        id, brand_name, molecule, strength, unit,
                        branded_price, generic_price, source, aliases,
                        brand_name_lower, molecule_lower
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item["id"],
                    item["brand_name"],
                    item["molecule"],
                    item["strength"],
                    item["unit"],
                    float(item["branded_price"]),
                    float(item["generic_price"]),
                    item["source"],
                    json.dumps(item.get("aliases", [])),
                    item["brand_name"].lower(),
                    item["molecule"].lower()
                ))
            conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db(force_reload=True)
    print("Database initialized successfully at", DEFAULT_DB_PATH)
