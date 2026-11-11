"""Aggregate nationwide JMA daily observations, retaining coverage and resort proximity."""
import csv,datetime,statistics,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
allrows=[]
for path in sorted((ROOT/"data").glob("jma_national_snow_history_batch_??.csv")):
 if "_status" in path.name:continue
 with path.open(encoding="utf-8",newline="") as f:allrows.extend(csv.DictReader(f))
if len(allrows)<25000:raise SystemExit("Incomplete nationwide 14-station input")
by=collections.defaultdict(list);names={}
for r in allrows:
 d=datetime.date.fromisoformat(r["date"]);winter=d.year if d.month>=11 else d.year-1
 by[(r["station_id"],winter)].append(r);names[r["station_id"]]=r["station_name"]
metrics=[]
for (sid,winter),rs in sorted(by.items()):
 expected=(datetime.date(winter+1,5,1)-datetime.date(winter,11,1)).days
 unique_dates={r["date"] for r in rs}
 if len(unique_dates)!=len(rs):raise ValueError(f"Duplicate dates {sid} {winter}")
 depths=[float(r["snow_depth_cm"]) for r in rs if r["snow_depth_cm"]!=""]
 coverage=len(depths)/expected
 metrics.append(dict(station_id=sid,station_name=names[sid],winter_start_year=winter,expected_days=expected,observed_days=len(rs),valid_depth_days=len(depths),coverage=round(coverage,4),snow_cover_days_1cm=sum(v>=1 for v in depths),snow_cover_days_30cm=sum(v>=30 for v in depths),max_snow_depth_cm=max(depths) if depths else "",mean_snow_depth_cm=round(statistics.mean(depths),2) if depths else "",quality_status="usable" if coverage>=0.9 else "incomplete"))
path=ROOT/"data/jma_national_winter_snow_metrics_2016_2025.csv"
with path.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(metrics[0]));w.writeheader();w.writerows(metrics)
with (ROOT/"data/national_jma_snow_station_candidates.csv").open(encoding="utf-8-sig",newline="") as f:links=list(csv.DictReader(f))
station_ids={r["station_id"] for r in metrics}
pairs=collections.defaultdict(list)
for r in links:
 if r["jma_station_id"] in station_ids:
  pairs[r["candidate_id"]].append(r)
closest=[min(v,key=lambda x:float(x["straight_line_distance_km"])) for v in pairs.values()]
out=ROOT/"data/resort_to_observed_jma_station_coverage.csv"
with out.open("w",encoding="utf-8",newline="") as f:
 w=csv.writer(f);w.writerow(["candidate_id","resort_name","jma_station_id","jma_station_name","distance_km","station_winters_usable"])
 for r in sorted(closest,key=lambda r:r["candidate_id"]):
  sid=r["jma_station_id"]
  w.writerow([r["candidate_id"],r["resort_name"],sid,r["jma_station_name"],r["straight_line_distance_km"],sum(m["station_id"]==sid and m["quality_status"]=="usable" for m in metrics)])
report=ROOT/"reports/national_jma_14_station_winter_coverage.md"
report.write_text(f"# Nationwide JMA ten-winter snow observation coverage\n\n- Actual daily records: {len(allrows):,}\n- Distinct stations: {len(station_ids)}\n- Winter-by-station records: {len(metrics)}\n- Usable complete winter series: {sum(r['quality_status']=='usable' for r in metrics)}\n- Resorts matched to at least one of the observed stations (among their 5 candidate nearest stations): {len(closest)}\n- Of those, within 10km: {sum(float(r['straight_line_distance_km'])<=10 for r in closest)}\n- Of those, within 20km: {sum(float(r['straight_line_distance_km'])<=20 for r in closest)}\n\nThis is an initial subset, not a national climate estimate. Resort coordinates and station proximity are provisional. Snow cover at a weather station is not actual ski resort operating days.\n",encoding="utf-8")
print(report.read_text())
