"""Reproducible complete-window sensitivity of climate slopes and land price change."""
import csv, math, statistics
from collections import defaultdict
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def read(path):
 with (P/path).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
coords=read("data/national_resort_osm_reconciliation.csv")
ids={r["resort_name"]:r["candidate_id"] for r in coords}
climate=defaultdict(dict)
for r in read("data/ski_region_reanalysis_climate_1986_2025.csv"):
 if r["mean_temperature_c"] and r["winter_snowfall_cm"]:
  climate[r["candidate_id"]][int(r["year"])]=(float(r["mean_temperature_c"]),float(r["winter_snowfall_cm"]))
land=read("data/ski_resort_observed_land_price_1996_2026.csv")
pairs={}
for r in land:
 if r["radius_km"]=="10" and r["year"]=="2026" and r["median_same_point_change_pct"] and int(r["matched_1996_2026_point_count"] or 0)>=5:
  pairs[r["candidate_id"]]=(r["resort_name"],float(r["median_same_point_change_pct"]))
def slope(years,values):
 xm=statistics.mean(years);ym=statistics.mean(values)
 return 10*sum((x-xm)*(y-ym) for x,y in zip(years,values))/sum((x-xm)**2 for x in years)
def corr(xs,ys):
 if len(xs)<3:return float("nan")
 xm=statistics.mean(xs);ym=statistics.mean(ys)
 den=math.sqrt(sum((x-xm)**2 for x in xs)*sum((y-ym)**2 for y in ys))
 return sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/den if den else float("nan")
lines=["# 完全年次系列に限定した気候・地価感度分析","",
"地価変動率は1996–2026年の同一地点名目価格中央値。気候はERA5の暦年年平均気温・暦年冬季積雪推計。観測期間ごとに全年度が揃う地域のみ採用。","",
"| 気象期間 | 結合地域数 | 気温と地価 Pearson r | 積雪と地価 Pearson r |","|---|---:|---:|---:|"]
for start,end in [(1986,2025),(1996,2025),(2006,2025),(2016,2025)]:
 vals=[]
 for cid,(name,price) in pairs.items():
  s=climate.get(cid,{})
  years=list(range(start,end+1))
  if any(y not in s for y in years):continue
  vals.append((price,slope(years,[s[y][0] for y in years]),slope(years,[s[y][1] for y in years])))
 if len(vals)>=3:
  lines.append(f"| {start}–{end} | {len(vals)} | {corr([v[0] for v in vals],[v[1] for v in vals]):+.3f} | {corr([v[0] for v in vals],[v[2] for v in vals]):+.3f} |")
lines.extend(["","## 解釈","気象期間の選択に対する感度が大きく、単純相関から温暖化の地価への因果効果は導けない。短期の気象傾向を長期の地価変化と結びつけることは不適切。",""])
out=P/"reports/climate_time_window_sensitivity_reproducible_ja.md"
out.write_text("\n".join(lines),encoding="utf-8")
print("Wrote",out)
