"""Exploratory national ski-area snow trend versus nearby land-price change.

This is a descriptive cross-sectional association, not causal identification.
Uses 10 usable JMA winters, 2016-2026 matched MLIT land points, >=5 price
points within 10/20 km, and a JMA station no farther than 20 km.
"""
import csv,statistics,math,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):
 with (ROOT/path).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
snow=read("data/jma_national_combined_winter_metrics_2016_2025.csv")
links=read("data/resort_to_national_jma_observed_snow_coverage.csv")
land=read("data/ski_resort_mlit_buffer_summary_2016_2026.csv")
by_station=collections.defaultdict(list)
for r in snow:
 if r["quality_status"]=="usable":by_station[r["station_id"]].append(r)
land_by={(r["candidate_id"],int(r["radius_km"])):r for r in land}
def trend(rs,key):
 ordered=sorted(rs,key=lambda r:int(r["winter_start_year"]))
 xs=[int(r["winter_start_year"]) for r in ordered]
 ys=[float(r[key]) for r in ordered]
 xm=statistics.mean(xs);ym=statistics.mean(ys)
 return sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/sum((x-xm)**2 for x in xs)
def corr(x,y):
 if len(x)<3:return None
 xm=statistics.mean(x);ym=statistics.mean(y)
 denom=math.sqrt(sum((a-xm)**2 for a in x)*sum((b-ym)**2 for b in y))
 return sum((a-xm)*(b-ym) for a,b in zip(x,y))/denom if denom else None
rows=[]
for r in links:
 sid=r["station_id"];series=by_station[sid]
 if len(series)!=10 or float(r["distance_km"])>20:continue
 for radius in (10,20):
  l=land_by.get((r["candidate_id"],radius))
  if not l or int(l["matched_same_points_2016_2026"])<5 or not l["median_change_pct"]:continue
  rows.append(dict(candidate_id=r["candidate_id"],resort_name=r["resort_name"],station_id=sid,station_name=r["station_name"],station_distance_km=r["distance_km"],land_radius_km=radius,land_matched_point_count=l["matched_same_points_2016_2026"],land_median_change_2016_2026_pct=l["median_change_pct"],snow_1cm_days_trend_per_year=round(trend(series,"snow_cover_days_1cm"),3),snow_30cm_days_trend_per_year=round(trend(series,"snow_cover_days_30cm"),3),snow_max_depth_trend_cm_per_year=round(trend(series,"maximum_snow_depth_cm"),3)))
out=ROOT/"data/ski_snow_land_exploratory_matched_2016_2026.csv"
fields=["candidate_id","resort_name","station_id","station_name","station_distance_km","land_radius_km","land_matched_point_count","land_median_change_2016_2026_pct","snow_1cm_days_trend_per_year","snow_30cm_days_trend_per_year","snow_max_depth_trend_cm_per_year"]
with out.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
lines=["# Exploratory nationwide ski-area snow trend and nearby land price change","","**This is descriptive and not evidence that shortened ski seasons cause land-price declines.**","",
"Eligibility: resort linked to JMA station within 20 km, all 10 winters usable (Nov–Apr, 2016–2025 winter starts), and at least 5 matched MLIT price points in each tested land-price radius.","",
"| Land radius | Eligible resorts | Pearson r: snow >=1cm days trend vs land price | Pearson r: snow >=30cm days trend vs land price |",
"|---|---:|---:|---:|"]
for radius in (10,20):
 subset=[r for r in rows if r["land_radius_km"]==radius]
 ys=[float(r["land_median_change_2016_2026_pct"]) for r in subset]
 a=corr([r["snow_1cm_days_trend_per_year"] for r in subset],ys)
 b=corr([r["snow_30cm_days_trend_per_year"] for r in subset],ys)
 lines.append(f"| {radius} km | {len(subset)} | {a:.3f} | {b:.3f} |" if a is not None and b is not None else f"| {radius} km | {len(subset)} | insufficient variation/sample | insufficient variation/sample |")
lines+=["","## Essential limitations","",
"- Ten winters are a short climate window; linear slopes are descriptive and noisy.",
"- JMA station snow days are **not** actual resort operating days. Operating-day series are not yet available.",
"- Ski resort coordinates are provisional and JMA station elevation may differ materially from ski slope elevation.",
"- The MLIT 2016–2026 matched-point cohort includes only 2026-surviving price points (survivorship bias).",
"- No adjustment for tourism demand, infrastructure, transport, urbanization, property type, elevation or resort closures.",
"- Multiple resorts may share the same JMA station and land-price points; rows are not statistically independent.",
"- Correlation here cannot establish temporal or causal effects; do not use p-values treating resort rows as independent.",
""]
report=ROOT/"reports/national_ski_snow_land_exploratory_association.md"
report.write_text("\n".join(lines),encoding="utf-8")
print(report.read_text())
