"""Join existing OSM-name-matched ski areas to 2026 MLIT land-price points.

This is a proximity exploration, not verified resort entrances or causal analysis.
Only official MLIT land prices are used; the ZIP is downloaded at run time.
"""
import csv,io,json,math,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MATCH=ROOT/"data/osm_directory_name_matches.csv"
MANIFEST=ROOT/"data/mlit_land_price_archive_manifest.csv"
OUTPUT=ROOT/"data/resort_landprice_nearest_2026.csv"
SUMMARY=ROOT/"reports/resort_landprice_proximity_2026.md"
def distance(lat1,lon1,lat2,lon2):
    p1,p2=math.radians(lat1),math.radians(lat2)
    a=math.sin((p2-p1)/2)**2+math.cos(p1)*math.cos(p2)*math.sin(math.radians(lon2-lon1)/2)**2
    return 12742*math.asin(min(1,math.sqrt(a)))
def main():
    with MATCH.open(encoding="utf-8",newline="") as f:resorts=list(csv.DictReader(f))
    with MANIFEST.open(encoding="utf-8",newline="") as f:
        url=next(r["archive_url"] for r in csv.DictReader(f) if r["year"]=="2026")
    if not url.startswith("https://nlftp.mlit.go.jp/ksj/"):raise SystemExit("Unexpected source host")
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=120) as response:
        data=response.read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        name=next(x for x in z.namelist() if x.endswith(".geojson"))
        features=json.loads(z.read(name)).get("features",[])
    points=[]
    for f in features:
        g=f.get("geometry") or {};p=f.get("properties") or {};c=g.get("coordinates") or []
        if g.get("type")=="Point" and len(c)>=2:
            try:points.append((float(c[1]),float(c[0]),p))
            except (TypeError,ValueError):continue
    if len(points)<20000:raise SystemExit(f"Unexpectedly few MLIT points: {len(points)}")
    output=[]
    for resort in resorts:
        lat=float(resort["latitude"]);lon=float(resort["longitude"])
        # Avoid a full sort on every point: retain only nearby candidates then sort.
        nearby=sorted(((distance(lat,lon,a,b),a,b,p) for a,b,p in points if abs(a-lat)<0.25 and abs(b-lon)<0.35),key=lambda t:t[0])[:5]
        for rank,(km,a,b,p) in enumerate(nearby,1):
            output.append({"resort_name":resort["directory_name"],"osm_name":resort["osm_name"],"osm_url":resort["osm_source_url"],"resort_latitude":lat,"resort_longitude":lon,"nearest_rank":rank,"distance_km":round(km,3),"mlit_latitude":a,"mlit_longitude":b,"mlit_municipality_code":p.get("L01_001",""),"mlit_point_code_2":p.get("L01_002",""),"mlit_point_code_3":p.get("L01_003",""),"mlit_2026_price_yen_m2":p.get("L01_008",""),"mlit_2026_change_pct_raw":p.get("L01_009",""),"quality_flag":"proximity_only_unverified_resort_center"})
    if not output:raise SystemExit("No proximity candidates found")
    OUTPUT.parent.mkdir(exist_ok=True)
    with OUTPUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(output[0]));w.writeheader();w.writerows(output)
    SUMMARY.parent.mkdir(exist_ok=True)
    SUMMARY.write_text(f"""# Preliminary 2026 land-price proximity matching

- Resort-name matched OSM candidates: {len(resorts)}
- Official 2026 MLIT land-price point features: {len(points)}
- Nearest-point candidate rows (up to five per resort): {len(output)}
- Source: {url}
- Output: `data/resort_landprice_nearest_2026.csv`

**Cautions:** OSM feature centers are not verified resort entrances; nearest land-price points may be in a different market or land-use category. L01_008 is 2026 land price (JPY/m²) subject to official schema confirmation. These are exploratory spatial joins, not evidence that climate change affects land prices. A historical panel and controls are required.
""",encoding="utf-8")
    print(f"Matched {len(resorts)} ski-area candidates to {len(output)} nearby land-price observations")
if __name__=="__main__":main()
