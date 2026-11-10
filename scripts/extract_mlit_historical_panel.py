"""Extract 1983-2026 historical L01 price panel from official 2026 GeoJSON.

L01_061 is a 44-character selection/availability string. L01_062 through
L01_105 contain annual prices for 1983 through 2026. A zero price is
treated as missing, never a zero-valued parcel. Preserve all raw identifiers.
"""
import csv,io,json,urllib.request,zipfile,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/"data/mlit_land_price_archive_manifest.csv").open(encoding="utf-8",newline="") as f:
    url=next(r["archive_url"] for r in csv.DictReader(f) if r["year"]=="2026")
if not url.startswith("https://nlftp.mlit.go.jp/ksj/"):raise SystemExit("Unexpected archive host")
req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
with urllib.request.urlopen(req,timeout=120) as response:blob=response.read()
with zipfile.ZipFile(io.BytesIO(blob)) as z:
    member=next(x for x in z.namelist() if x.endswith(".geojson"))
    features=json.loads(z.read(member)).get("features",[])
if len(features)<20000:raise SystemExit("Unexpected number of source points")
out=ROOT/"data/mlit_landprice_historical_panel_1983_2026.csv"
counts=collections.Counter();invalid=collections.Counter()
fields=["municipality_code","point_id_2","point_id_3","latitude","longitude","land_use_raw","year","price_yen_m2","selection_flag","source_year","source_archive"]
with out.open("w",encoding="utf-8",newline="") as file:
    writer=csv.DictWriter(file,fieldnames=fields);writer.writeheader()
    for f in features:
        p=f.get("properties") or {};geo=f.get("geometry") or {};coord=geo.get("coordinates") or []
        if geo.get("type")!="Point" or len(coord)<2:invalid["bad_geometry"]+=1;continue
        flags=str(p.get("L01_061") or "")
        if len(flags)!=44:invalid["unexpected_selection_flag_length"]+=1
        for year in range(1983,2027):
            index=year-1983
            raw=p.get(f"L01_{62+index:03d}")
            try:price=float(raw)
            except (TypeError,ValueError):continue
            if price<=0:continue
            selection=flags[index] if len(flags)==44 else ""
            writer.writerow({"municipality_code":p.get("L01_001",""),"point_id_2":p.get("L01_002",""),"point_id_3":p.get("L01_003",""),"latitude":coord[1],"longitude":coord[0],"land_use_raw":p.get("L01_028",""),"year":year,"price_yen_m2":price,"selection_flag":selection,"source_year":2026,"source_archive":"L01-26_GML.zip"})
            counts[year]+=1
        # The 2026 historical column should agree with the current price.
        try:
            if float(p.get("L01_105"))!=float(p.get("L01_008")):invalid["2026_price_mismatch"]+=1
        except (TypeError,ValueError):invalid["2026_price_unavailable"]+=1
if not counts or counts[2026]<20000 or invalid["2026_price_mismatch"]:
    raise SystemExit(f"Historical column integrity check failed: {dict(invalid)}; 2026 count {counts[2026]}")
report=ROOT/"reports/mlit_historical_panel_audit.md"
report.write_text("# Official MLIT 1983–2026 historical price panel\n\n"+
    f"- Source: {url}\n- 2026 source features: {len(features)}\n"+
    f"- Extracted positive-price point-year records: {sum(counts.values())}\n"+
    f"- Observed years: {min(counts)}–{max(counts)}\n"+
    f"- 2026 records: {counts[2026]}\n"+
    f"- 2026 historical-vs-current mismatches: {invalid['2026_price_mismatch']}\n"+
    f"- Data quality flags: {dict(invalid)}\n\n"+
    "The 2026 archive supplies historical annual price fields L01_062–L01_105. "+
    "The L01_061 selection string is preserved for audit. A zero or missing value "+
    "is excluded rather than interpreted as a zero land price. "+
    "Historical records are attached to the 2026 survey-point sample: sites that "+
    "disappeared before 2026 may be absent (survivorship bias). "+
    "Do not use this panel as a balanced, representative municipality price index "+
    "without validating survey-point continuity and selection.\n\n"+
    "## Annual observation counts\n\n| Year | Positive-price records |\n|---|---:|\n"+
    "".join(f"| {year} | {counts[year]} |\n" for year in range(1983,2027)),encoding="utf-8")
print(f"Saved {sum(counts.values())} point-years; 2026 {counts[2026]}; warnings {dict(invalid)}")
