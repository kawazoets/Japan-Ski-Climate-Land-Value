"""Validate sourced ski season sample without equating span to actual open days."""
import csv
from datetime import date
from pathlib import Path
path=Path(__file__).resolve().parents[1]/"data"/"season_observations_2025_26_sample.csv"
with path.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
seen=set()
for row in rows:
    key=(row["resort_name"],row["season"])
    assert key not in seen, f"Duplicate: {key}"
    seen.add(key)
    start=date.fromisoformat(row["first_operating_date"])
    end=date.fromisoformat(row["last_operating_date"])
    assert (end-start).days+1==int(row["calendar_span_days"]), f"Incorrect calendar span: {key}"
    assert row["source_url"].startswith("https://"), f"Missing provenance: {key}"
    assert not row["actual_operating_days"], "Do not invent actual operating days"
print(f"Validated {len(rows)} sourced resort-season observations.")
