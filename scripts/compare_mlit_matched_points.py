"""Matched-site 2016–2026 price change by municipality and land-use.

Uses only points with both years observed in the same 2026 MLIT record.
Descriptive matched-site panel; not a municipality-wide constant-quality index.
"""
import csv,io,json,statistics,urllib.request,zipfile
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/"data/mlit_land_price_archive_manifest.csv").open(encoding="utf-8",newline="") as f:
    url=next(r["archive_url"] for r in csv.DictReader(f) if r["year"]=="2026")
if not url.startswith("https://nlftp.mlit.go.jp/ksj/"):raise SystemExit("Unexpected archive host")
with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=120) as r:blob=r.read()
with zipfile.ZipFile(io.BytesIO(blob)) as z:
    name=next(n for n in z.namelist() if n.endswith(".geojson"))
    features=json.loads(z.read(name)).get("features",[])
if len(features)<20000:raise SystemExit("Unexpectedly few records")
# 1983 corresponds to L01_062; 2016 corresponds to L01_095; 2026 to L01_105.
groups=defaultdict(list)
valid=0
for feature in features:
    p=feature.get("properties") or {}
    municipality=str(p.get("L01_001") or "")
    land_use=str(p.get("L01_028") or "")
    if len(municipality)!=5:continue
    try:
        old=float(p.get("L01_095"));new=float(p.get("L01_105"))
    except (ValueError,TypeError):continue
    if old<=0 or new<=0:continue
    valid+=1
    groups[(municipality,land_use)].append((old,new))
out=ROOT/"data/mlit_municipality_matched_2016_2026.csv"
fields=["municipality_code","land_use_raw","matched_point_count","median_price_2016_yen_m2","median_price_2026_yen_m2","median_point_change_pct","median_of_price_ratios_pct","status"]
with out.open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for (municipality,land_use),values in sorted(groups.items()):
        before=[a for a,b in values];after=[b for a,b in values]
        changes=[(b/a-1)*100 for a,b in values]
        w.writerow({"municipality_code":municipality,"land_use_raw":land_use,"matched_point_count":len(values),"median_price_2016_yen_m2":round(statistics.median(before),1),"median_price_2026_yen_m2":round(statistics.median(after),1),"median_point_change_pct":round(statistics.median(changes),3),"median_of_price_ratios_pct":round((statistics.median(after)/statistics.median(before)-1)*100,3),"status":"exploratory" if len(values)<5 else "five_or_more_matched_points"})
report=ROOT/"reports/mlit_matched_2016_2026_audit.md"
report.write_text(f"""# Matched survey-point price change, 2016–2026

- Source: {url}
- 2026 source survey points: {len(features)}
- Points with positive prices in **both 2016 and 2026**: {valid}
- Municipality × current land-use groups with matched points: {len(groups)}
- Groups with at least five matched points: {sum(len(v)>=5 for v in groups.values())}
- Output: `data/mlit_municipality_matched_2016_2026.csv`

`median_point_change_pct` is the median of individual matched-point percentage changes, whereas `median_of_price_ratios_pct` is the percentage change in the two cross-sectional medians for those same points. They need not agree.

**Limitations:** This conditions on a point appearing in the 2026 file, so earlier-closed points are omitted. Current land-use is used for grouping, not necessarily historical land-use. Nominal prices are not inflation-adjusted. A municipality with few matched points cannot support a stable local trend. No ski-resort exposure, weather data or causal identification is included yet.
""",encoding="utf-8")
print(f"Matched points: {valid}; municipality/use groups: {len(groups)}")
