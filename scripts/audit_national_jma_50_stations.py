"""Audit downloaded national JMA snow history station files and resort proximity."""
import csv,collections,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/"data/jma_station_history"
statuses=[];issues=[];all_ids=set()
for f in sorted(folder.glob("*_status.csv")):
 with f.open(encoding="utf-8-sig",newline="") as inp:
  records=list(csv.DictReader(inp))
 if len(records)!=1:issues.append(f"{f.name}: status row count {len(records)}");continue
 r=records[0];statuses.append(r);sid=r["station_id"]
 if sid in all_ids:issues.append(f"{sid}: duplicate station status")
 all_ids.add(sid)
 data=folder/f"{sid}.csv"
 if not data.exists():issues.append(f"{sid}: missing daily file");continue
 with data.open(encoding="utf-8-sig",newline="") as inp:rows=list(csv.DictReader(inp))
 if len(rows)!=int(r["daily_rows"]):issues.append(f"{sid}: daily count disagrees with status")
 if len({x["date"] for x in rows})!=len(rows):issues.append(f"{sid}: duplicate date")
 if any(x["station_id"]!=sid for x in rows):issues.append(f"{sid}: mismatched station ID")
 if int(r["complete_winters"])+int(r["failed_winters"])!=10:issues.append(f"{sid}: season counts not 10")
with (ROOT/"data/national_jma_snow_station_candidates.csv").open(encoding="utf-8-sig",newline="") as inp:links=list(csv.DictReader(inp))
matched=collections.defaultdict(list)
for r in links:
 if r["jma_station_id"] in all_ids:matched[r["candidate_id"]].append(r)
near={cid:min(float(x["straight_line_distance_km"]) for x in rs) for cid,rs in matched.items()}
out=ROOT/"reports/national_jma_50_station_download_audit.md"
out.write_text("# National JMA 50-station historical snow collection audit\n\n"+
 f"- Station status files: {len(statuses)}\n"+
 f"- Stations with ten complete winters: {sum(int(x['complete_winters'])==10 for x in statuses)}\n"+
 f"- Stations with one or more failed winters: {sum(int(x['failed_winters'])>0 for x in statuses)}\n"+
 f"- Recorded daily observations: {sum(int(x['daily_rows']) for x in statuses):,}\n"+
 f"- Ski resort candidates with at least one downloaded station among 5 nearest: {len(matched)}\n"+
 f"- Those with station within 10km: {sum(d<=10 for d in near.values())}\n"+
 f"- Those with station within 20km: {sum(d<=20 for d in near.values())}\n"+
 f"- Integrity issues: {len(issues)}\n\n"+
 ("## Issues\n"+"\n".join("- "+i for i in issues)+"\n" if issues else "")+
 "\nThis is an observational coverage audit, not a resort operating-day or land-price causal result.\n",encoding="utf-8")
print(out.read_text())
if issues:raise SystemExit("Data integrity issues detected")
