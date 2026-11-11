"""Audit national JMA observations in both first and priority batches.

Count actual data files, complete winters, unique stations, and resort proximity.
Do not treat successful GitHub jobs as proof that every station has complete data.
"""
import csv,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
dirs=[ROOT/"data/jma_station_history",ROOT/"data/jma_priority_station_history"]
stations={};issues=[];sources=collections.Counter()
for folder in dirs:
 for file in sorted(folder.glob("*_status.csv")):
  with file.open(encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
  if len(rows)!=1:issues.append(f"Bad status file: {file}");continue
  r=rows[0];sid=r["station_id"];sources[folder.name]+=1
  daily=folder/f"{sid}.csv"
  if not daily.exists():issues.append(f"Missing daily file {daily}");continue
  with daily.open(encoding="utf-8-sig",newline="") as f:records=list(csv.DictReader(f))
  if len(records)!=int(r["daily_rows"]):issues.append(f"Count mismatch {sid}")
  if len({v["date"] for v in records})!=len(records):issues.append(f"Duplicate dates {sid}")
  if sid in stations:
   prev=stations[sid]
   if len(records)>prev["count"]:stations[sid]={"count":len(records),"complete":int(r["complete_winters"]),"name":r["station_name"]}
  else:stations[sid]={"count":len(records),"complete":int(r["complete_winters"]),"name":r["station_name"]}
with (ROOT/"data/national_jma_snow_station_candidates.csv").open(encoding="utf-8-sig",newline="") as f:links=list(csv.DictReader(f))
proximity=collections.defaultdict(list)
for r in links:
 if r["jma_station_id"] in stations:proximity[r["candidate_id"]].append(float(r["straight_line_distance_km"]))
nearest={cid:min(ds) for cid,ds in proximity.items()}
total=sum(v["count"] for v in stations.values())
complete=sum(v["complete"]==10 for v in stations.values())
failed=[(sid,v) for sid,v in stations.items() if v["complete"]<10]
lines=["# Nationwide observed snow coverage after first and priority batches","",
f"- First-batch status files: {sources['jma_station_history']}",
f"- Priority-batch status files: {sources['jma_priority_station_history']}",
f"- Unique station IDs with actual downloaded files: {len(stations)}",
f"- Stations with all ten winters: {complete}",
f"- Stations with incomplete winter histories: {len(failed)}",
f"- Daily records across unique station IDs: {total:,}",
f"- Resort candidates with any of their 5 nearest stations observed: {len(nearest)}",
f"- Resort candidates within 10 km of observed station: {sum(d<=10 for d in nearest.values())}",
f"- Resort candidates within 20 km of observed station: {sum(d<=20 for d in nearest.values())}",
f"- Integrity issues: {len(issues)}","",
"## Incomplete stations",""]
lines.extend(f"- {sid} {v['name']}: {v['complete']}/10 winters, {v['count']} days" for sid,v in failed)
lines+=["","## Data integrity issues",""]
lines.extend("- "+s for s in issues)
lines+=["","**Limitations:** Coordinates are provisional; weather-station snow days are not actual ski operating days; this report does not estimate a causal land-price effect.",""]
path=ROOT/"reports/national_jma_100_station_coverage_audit.md"
path.write_text("\n".join(lines),encoding="utf-8")
print(path.read_text())
if issues:raise SystemExit("Data integrity issues detected")
