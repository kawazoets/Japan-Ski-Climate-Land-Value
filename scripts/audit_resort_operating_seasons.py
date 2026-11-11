"""Validate source-backed ski-resort operating seasons, without inferring days.

Dates are inclusive; calendar span is not actual operating days.
Only independently evidenced observed_operating_days is usable as an operating-day outcome.
"""
import csv,datetime,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=ROOT/"data/resort_operating_season_evidence.csv"
 with p.open(encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
 required={"candidate_id","season_start_year","first_open_date","last_open_date","observed_operating_days","source_url","source_type","evidence_status","notes"}
 if not required.issubset(rows[0] if rows else set(csv.DictReader(p.open(encoding="utf-8-sig")).fieldnames or [])):raise SystemExit("Operating season schema mismatch")
 issues=[];valid=[];seen=set()
 for idx,r in enumerate(rows,2):
  try:
   k=(r["candidate_id"],int(r["season_start_year"]))
   if k in seen:issues.append(f"row {idx}: duplicate candidate/season")
   seen.add(k)
   if not 2016<=k[1]<=2026:issues.append(f"row {idx}: season out of range")
   start=datetime.date.fromisoformat(r["first_open_date"]) if r["first_open_date"] else None
   end=datetime.date.fromisoformat(r["last_open_date"]) if r["last_open_date"] else None
   if start and end and end<start:issues.append(f"row {idx}: negative calendar span")
   if start and start.year not in (k[1],k[1]+1):issues.append(f"row {idx}: start outside season")
   if end and end.year not in (k[1],k[1]+1):issues.append(f"row {idx}: end outside season")
   days=int(r["observed_operating_days"]) if r["observed_operating_days"] else None
   if days is not None and not 0<=days<=366:issues.append(f"row {idx}: invalid operating days")
   if days is not None and start and end and days>(end-start).days+1:issues.append(f"row {idx}: days exceed calendar span")
   if days is not None and (not r["source_url"].startswith("https://") or r["evidence_status"]!="verified"):issues.append(f"row {idx}: operating days lack verified source")
   if days is not None and r["evidence_status"]=="verified":valid.append(r)
  except (ValueError,KeyError) as e:issues.append(f"row {idx}: {e}")
 report=ROOT/"reports/resort_operating_season_evidence_audit.md"
 report.write_text("# Ski resort operating-season evidence audit\n\n"+f"- Evidence rows: {len(rows)}\n- Verified operating-day records: {len(valid)}\n- Issues: {len(issues)}\n\n"+"\n".join("- "+s for s in issues[:100])+"\n\n**Calendar opening-to-closing span is not actual operating days.** No unverified values are imputed.\n",encoding="utf-8")
 print(report.read_text())
 if issues:raise SystemExit("Evidence validation failed")
if __name__=="__main__":main()
