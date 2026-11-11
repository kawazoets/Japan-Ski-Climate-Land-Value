"""Validate source-backed ski operating seasons. Never infer days from snow depth."""
import csv,datetime,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data/resort_operating_season_evidence.csv"
FIELDS=["candidate_id","season_start_year","first_open_date","last_open_date","observed_operating_days","source_url","source_type","evidence_status","notes"]
def read(p):
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def main():
    if not SOURCE.exists():
        SOURCE.parent.mkdir(exist_ok=True)
        with SOURCE.open("w",encoding="utf-8",newline="") as f:
            csv.writer(f).writerow(FIELDS)
    raw=read(SOURCE)
    ids={r["candidate_id"] for r in read(ROOT/"data/national_resort_osm_reconciliation.csv")}
    valid=[];issues=[];seen=set()
    for n,r in enumerate(raw,2):
        try:
            if r["candidate_id"] not in ids:raise ValueError("unknown candidate_id")
            year=int(r["season_start_year"])
            if not 2015<=year<=2026:raise ValueError("season outside target window")
            key=(r["candidate_id"],year)
            if key in seen:raise ValueError("duplicate resort-season")
            seen.add(key)
            start=datetime.date.fromisoformat(r["first_open_date"]) if r["first_open_date"] else None
            end=datetime.date.fromisoformat(r["last_open_date"]) if r["last_open_date"] else None
            if start and not year<=start.year<=year+1:raise ValueError("opening date outside season")
            if end and not year<=end.year<=year+1:raise ValueError("closing date outside season")
            if start and end and end<start:raise ValueError("closing before opening")
            days=int(r["observed_operating_days"]) if r["observed_operating_days"] else None
            if days is not None and not 0<=days<=366:raise ValueError("invalid operating days")
            if days is not None and start and end and days>(end-start).days+1:raise ValueError("days exceed calendar span")
            if not r["source_url"].startswith(("https://","http://")):raise ValueError("missing source URL")
            if r["evidence_status"] not in ("primary_source_verified","secondary_source_unverified","needs_manual_review"):raise ValueError("invalid evidence status")
            valid.append(r)
        except (ValueError,KeyError) as e:issues.append(f"line {n}: {e}")
    report=ROOT/"reports/operating_season_evidence_audit.md"
    report.write_text("# Ski-area operating season evidence audit\n\n"+
        f"- Candidate ski areas in cohort: **{len(ids)}**\n"+
        f"- Source-backed resort-season rows: **{len(valid)}**\n"+
        f"- Rows with observed operating-day counts: **{sum(bool(r['observed_operating_days']) for r in valid)}**\n"+
        f"- Validation issues: **{len(issues)}**\n\n"+
        ("## Issues\n\n"+"\n".join("- "+x for x in issues)+"\n\n" if issues else "")+
        "Opening-to-closing calendar span is not actual operating days. Missing dates or days are retained as missing. Resort closures must be documented with date-specific sources.\n",encoding="utf-8")
    print(report.read_text(encoding="utf-8"))
    if issues:raise SystemExit("Invalid source-backed season rows")
if __name__=="__main__":main()
