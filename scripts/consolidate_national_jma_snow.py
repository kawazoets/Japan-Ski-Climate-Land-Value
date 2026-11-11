"""Combine verified ten-winter JMA station files across all three download batches.

Prefer the station copy with most complete winters. Emit one station-winter
metric only if at least 90% of calendar days have valid snow observations.
"""
import csv,datetime,collections,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
folders=["jma_station_history","jma_priority_station_history","jma_synoptic_station_history"]
chosen={}
for dirname in folders:
 folder=ROOT/"data"/dirname
 for status in folder.glob("*_status.csv"):
  with status.open(encoding="utf-8-sig",newline="") as f:rs=list(csv.DictReader(f))
  if len(rs)!=1:continue
  r=rs[0];sid=r["station_id"]
  score=(int(r["complete_winters"]),int(r["daily_rows"]))
  if sid not in chosen or score>chosen[sid][0]:chosen[sid]=(score,folder/f"{sid}.csv",r)
rows=[];usable=0;bad=[]
for sid,(_,path,st) in sorted(chosen.items()):
 with path.open(encoding="utf-8-sig",newline="") as f:daily=list(csv.DictReader(f))
 grouped=collections.defaultdict(list)
 for r in daily:
  d=datetime.date.fromisoformat(r["date"])
  grouped[d.year if d.month>=11 else d.year-1].append(r)
 for winter in range(2016,2026):
  records=grouped[winter];expected=(datetime.date(winter+1,5,1)-datetime.date(winter,11,1)).days
  values=[float(r["snow_depth_cm"]) for r in records if r["snow_depth_cm"] not in ("","-","--")]
  coverage=len(values)/expected
  status="usable" if len(records)==expected and coverage>=0.9 else "incomplete"
  usable+=status=="usable"
  rows.append(dict(station_id=sid,station_name=st["station_name"],winter_start_year=winter,expected_days=expected,recorded_days=len(records),valid_snow_depth_days=len(values),coverage=round(coverage,4),snow_cover_days_1cm=sum(v>=1 for v in values),snow_cover_days_30cm=sum(v>=30 for v in values),maximum_snow_depth_cm=max(values) if values else "",mean_snow_depth_cm=round(statistics.mean(values),2) if values else "",quality_status=status))
  if status!="usable":bad.append(f"{sid} {st['station_name']} {winter}: records={len(records)}, valid={len(values)}")
out=ROOT/"data/jma_national_combined_winter_metrics_2016_2025.csv"
with out.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with (ROOT/"data/national_jma_snow_station_candidates.csv").open(encoding="utf-8-sig",newline="") as f:links=list(csv.DictReader(f))
valid_ids={r["station_id"] for r in rows if r["quality_status"]=="usable"}
by_resort=collections.defaultdict(list)
for r in links:
 if r["jma_station_id"] in valid_ids:by_resort[r["candidate_id"]].append(r)
matched={cid:min(rs,key=lambda r:float(r["straight_line_distance_km"])) for cid,rs in by_resort.items()}
coverage=ROOT/"data/resort_to_national_jma_observed_snow_coverage.csv"
with coverage.open("w",encoding="utf-8",newline="") as f:
 w=csv.writer(f);w.writerow(["candidate_id","resort_name","station_id","station_name","distance_km","usable_winters"])
 for cid,r in sorted(matched.items()):
  sid=r["jma_station_id"];w.writerow([cid,r["resort_name"],sid,r["jma_station_name"],r["straight_line_distance_km"],sum(x["station_id"]==sid and x["quality_status"]=="usable" for x in rows)])
report=ROOT/"reports/national_jma_combined_2016_2025_results.md"
report.write_text(f"# Combined nationwide JMA snow-depth observation results\n\n- Unique stations with downloaded records: {len(chosen)}\n- Stations with all 10 winters usable: {sum(all(r['quality_status']=='usable' for r in rows if r['station_id']==sid) for sid in chosen)}\n- Usable station-winters: {usable} / {len(rows)}\n- Resort candidates linked to at least one station with usable winters: {len(matched)}\n- Linked resorts within 10 km: {sum(float(r['straight_line_distance_km'])<=10 for r in matched.values())}\n- Linked resorts within 20 km: {sum(float(r['straight_line_distance_km'])<=20 for r in matched.values())}\n\n## Incomplete station-winters\n\n"+"\n".join("- "+x for x in bad[:100])+"\n\nThese are station snow observations, not actual ski resort operating days. Resort coordinates are provisional.\n",encoding="utf-8")
print(report.read_text()[:6000])
