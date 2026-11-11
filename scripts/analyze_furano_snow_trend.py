"""Generate reproducible descriptive trends from actual JMA winter-season records.

A ten-year trend at one valley weather station is not a nationwide ski-area
climate trend and cannot establish a causal effect on nearby land prices.
"""
import csv,statistics,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/"data/jma_snow_winter_season_metrics_2016_2025.csv"
with source.open(encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
if len(rows)!=10 or {int(r["winter_start_year"]) for r in rows}!=set(range(2016,2026)):raise SystemExit("Expected exactly 10 complete Furano winters")
if {r["station_id"] for r in rows}!={"12940"}:raise SystemExit("Unexpected station")
if any(r["quality_status"]!="usable" or float(r["coverage"])<0.9 for r in rows):raise SystemExit("Incomplete winter")
years=[int(r["winter_start_year"]) for r in rows]
def slope(vals):
 x=years;xm=statistics.mean(x);ym=statistics.mean(vals)
 return sum((a-xm)*(b-ym) for a,b in zip(x,vals))/sum((a-xm)**2 for a in x)
metrics=[("Snow cover >=1cm (days)","observed_snow_cover_days_1cm"),("Snow cover >=30cm (days)","observed_snow_cover_days_30cm"),("Maximum daily snow depth (cm)","max_daily_snow_depth_cm"),("Mean daily snow depth (cm)","mean_observed_depth_cm")]
lines=["# Furano official JMA snow-depth trends: 2016–2025 winter starts","","Station 12940 (富良野), observed November–April; ten complete winters.","","| Measure | 2016 winter | 2025 winter | 2016–20 mean | 2021–25 mean | Linear slope per year |","|---|---:|---:|---:|---:|---:|"]
for label,key in metrics:
 vals=[float(r[key]) for r in rows]
 lines.append(f"| {label} | {vals[0]:.1f} | {vals[-1]:.1f} | {statistics.mean(vals[:5]):.1f} | {statistics.mean(vals[5:]):.1f} | {slope(vals):+.2f} |")
lines+=["","## Interpretation limits","","- The slope is an unadjusted ordinary least squares descriptive estimate over only ten winter seasons; no significance or causal claim is made.","- A valley station is not necessarily representative of the mountain ski slopes, even if geographically nearby.","- Snow-cover days are measured at the weather station, **not** days a resort was open.","- No resort operating-day evidence is yet linked; no snow-to-land-price inference is supported.","- Only November–April is counted; any May or October operating days are excluded.","","Source: `data/jma_snow_winter_season_metrics_2016_2025.csv` and official JMA daily observations in `data/jma_daily_snow_depth_2016_2026.csv`."]
target=ROOT/"reports/furano_snow_trend_2016_2025.md"
target.write_text("\n".join(lines)+"\n",encoding="utf-8")
print(target.read_text())
