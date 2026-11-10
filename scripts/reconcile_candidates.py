"""Generate an auditable count reconciliation report from candidate classes."""
import csv
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/"data"/"directory_classified.csv"
with source.open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f))
counts=Counter(r["candidate_class"] for r in rows)
report=f"""# Resort candidate reconciliation

Generated from `data/directory_classified.csv`.

| Class | Entries |
|---|---:|
| Operating status unverified | {counts['operating_unverified']} |
| Possibly closed | {counts['possibly_closed']} |
| Non-resort navigation | {counts['non_resort_navigation']} |
| Total candidate rows | {len(rows)} |

The 417 resort count is from a different source and methodology. **The {counts['operating_unverified']} entries are NOT verified as operating, and the difference from 417 is not evidence of any particular closure count.**

## Next evidence needed
1. Official facility-level roster and exact definition of the 417 count.
2. Verified name/municipality coordinates and closure dates.
3. Resort-specific historical season dates.
4. Land price points from MLIT with year and land-use classifications.

This report intentionally avoids unsupported quantitative climate or land-value conclusions.
"""
out=ROOT/"reports"/"candidate_reconciliation.md";out.parent.mkdir(exist_ok=True);out.write_text(report,encoding="utf-8")
print(report)
