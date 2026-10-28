"""Load fictional sample batteries into the database.

Usage: python -m scripts.seed
Safe to run repeatedly: batteries that already exist are skipped.
"""

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app import crud
from app.database import SessionLocal, create_tables
from app.schemas import BatteryCreate

SAMPLE_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_batteries.json"


def seed(db: Session, path: Path = SAMPLE_FILE) -> tuple[int, int]:
    """Insert sample batteries. Returns (inserted, skipped)."""
    records = json.loads(path.read_text(encoding="utf-8"))
    inserted = skipped = 0
    for record in records:
        # Validate through the same schema the API uses.
        data = BatteryCreate.model_validate(record)
        try:
            crud.create_battery(db, data)
            inserted += 1
        except crud.DuplicateBatteryError:
            skipped += 1
    return inserted, skipped


def main() -> None:
    create_tables()
    with SessionLocal() as db:
        inserted, skipped = seed(db)
    print(f"Seed complete: {inserted} inserted, {skipped} skipped (already present).")


if __name__ == "__main__":
    main()
