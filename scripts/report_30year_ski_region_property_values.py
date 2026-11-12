import csv,collections,statistics
from pathlib import Path
P=Path(__file__).resolve().parents[1]
with (P/"data/ski_resort_observed_land_price_1996_2026.csv").open(encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
regions=collections.defaultdict(dict)
for r in rows:
 if int(r["radius_km"])==10:regions[r["candidate_id"]][int(r["year"])]=r
eligible=[]
for cid,years in regions.items():
 a=years.get(1996);b=years.get(2026)
 if not a or not b:continue
 n=int(b["matched_1996_2026_point_count"] or 0)
 if n<5 or not b["median_same_point_change_pct"]:continue
 eligible.append((float(b["median_same_point_change_pct"]),n,b["resort_name"],cid,a,b))
eligible.sort()
def table(records):
 return "\n".join(f"| {name} | {change:+.1f}% | {n} |" for change,n,name,cid,a,b in records)
report=P/"reports/30year_ski_region_property_value_findings.md"
positive=sum(x[0]>0 for x in eligible);negative=sum(x[0]<0 for x in eligible);flat=len(eligible)-positive-negative
lines=["# 1996–2026: 30-year ski-region land-value findings","",
"## What the observed land-price records establish","",
f"- Resort candidates with provisional geocodes and annual spatial records: {len(regions)}.",
f"- At 10 km, resorts with >=5 identical land-price points observed in both 1996 and 2026: {len(eligible)}.",
f"- Positive 30-year median same-point change: {positive}; negative: {negative}; unchanged: {flat}.",
f"- Median of eligible resort-level 30-year price changes: {statistics.median(x[0] for x in eligible):+.1f}%." if eligible else "- No eligible resort regions.","",
"## Largest observed declines (10 km, >=5 matched points)","","| Resort region | 1996–2026 median same-point change | Matched points |","|---|---:|---:|",table(eligible[:15]),"",
"## Largest observed gains (10 km, >=5 matched points)","","| Resort region | 1996–2026 median same-point change | Matched points |","|---|---:|---:|",table(list(reversed(eligible[-15:]))),"",
"## What this does NOT establish","",
"- These are nominal yen/m² changes, not inflation-adjusted real property values.",
"- Observations are from 2026-surviving survey points only. Resort positions are provisional; nearby resorts may share points.",
"- Land use, proximity to cities, foreign investment, tourism and population have not been controlled.",
"- **No 30-year climate association or causal warming effect has yet been calculated.** These results establish spatially uneven property-value changes, not their causes.",
"- Interpret the extremes as candidates for follow-up investigation, not a ranking of climate impacts.",
""]
report.write_text("\n".join(lines),encoding="utf-8")
print("Eligible",len(eligible),"up",positive,"down",negative,"median",statistics.median(x[0] for x in eligible) if eligible else None)
