"""Municipality-level 2026 MLIT L01 land-price baseline.

Download official 2026 archive and summarize by municipality code and land use.
No historical-year interpretation until L01_061..148 dictionary is validated.
"""
import csv,io,json,statistics,urllib.request,zipfile
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/"data/mlit_land_price_archive_manifest.csv").open(encoding="utf-8",newline="") as f:
    url=next(r["archive_url"] for r in csv.DictReader(f) if r["year"]=="2026")
if not url.startswith("https://nlftp.mlit.go.jp/ksj/"):raise SystemExit("Unexpected download host")
req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
with urllib.request.urlopen(req,timeout=120) as response:blob=response.read()
with zipfile.ZipFile(io.BytesIO(blob)) as z:
    name=next(x for x in z.namelist() if x.endswith(".geojson"))
    features=json.loads(z.read(name)).get("features",[])
if len(features)<20000:raise SystemExit("Unexpectedly few MLIT features")
groups=defaultdict(list)
bad=0
for f in features:
    p=f.get("properties") or {}
    municipality=str(p.get("L01_001") or "").strip()
    land_use=str(p.get("L01_028") or "").strip()
    try:price=float(p.get("L01_008"))
    except (ValueError,TypeError):bad+=1;continue
    if len(municipality)!=5 or price<=0:bad+=1;continue
    groups[(municipality,land_use)].append(price)
if not groups:raise SystemExit("No municipality price groups")
out=ROOT/"data/mlit_municipality_landuse_2026.csv"
out.parent.mkdir(exist_ok=True)
with out.open("w",encoding="utf-8",newline="") as f:
    fields=["year","municipality_code","land_use_raw","survey_point_count","median_yen_per_m2","mean_yen_per_m2","minimum_yen_per_m2","maximum_yen_per_m2","source"]
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for (municipality,land_use),prices in sorted(groups.items()):
        w.writerow({"year":2026,"municipality_code":municipality,"land_use_raw":land_use,"survey_point_count":len(prices),"median_yen_per_m2":round(statistics.median(prices),1),"mean_yen_per_m2":round(statistics.mean(prices),1),"minimum_yen_per_m2":min(prices),"maximum_yen_per_m2":max(prices),"source":"MLIT L01-26_GML.zip"})
report=ROOT/"reports/municipality_landprice_2026.md"
report.write_text(f"""# Municipality × land-use baseline (2026)

Source: {url}

- Official point features: {len(features)}
- Valid positive-price points: {sum(map(len,groups.values()))}
- Excluded malformed/missing-price points: {bad}
- Municipality × land-use groups: {len(groups)}
- CSV: `data/mlit_municipality_landuse_2026.csv`

The grouping uses L01_001 (municipality code), L01_028 (land-use label), and L01_008 (2026 price per m²). Medians are descriptive, not transaction prices or constant-quality price indices. Municipality-level comparison must control for sample composition and land use; it is not yet a longitudinal climate impact estimate.
""",encoding="utf-8")
print(f"Saved {len(groups)} municipality × land-use groups from {len(features)} points")
