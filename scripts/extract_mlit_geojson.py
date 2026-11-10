"""Download official MLIT 2026 L01 GeoJSON and extract audited sample records.

No extra dependencies; stream ZIP contents into memory only for one 84MB GeoJSON.
Full output is a GitHub Actions artifact, not a repository commit.
"""
import csv,io,json,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/"data/mlit_land_price_archive_manifest.csv").open(encoding="utf-8") as f:
    url=next(r["archive_url"] for r in csv.DictReader(f) if r["year"]=="2026")
req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
with urllib.request.urlopen(req,timeout=120) as resp:raw=resp.read()
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    path=next(n for n in z.namelist() if n.endswith(".geojson"))
    data=json.loads(z.read(path))
features=data.get("features",[])
if not features:raise SystemExit("No GeoJSON features")
fields={}
for f in features:
    for key,val in f.get("properties",{}).items():
        if key not in fields:fields[key]=str(val)[:100]
meta={"feature_count":len(features),"property_examples":fields,"geometry_type_first":features[0].get("geometry",{}).get("type"),"source_archive_url":url}
out=ROOT/"reports/mlit_geojson_schema.json"
out.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
# Preserve source property keys without making assumptions about coded fields.
dest=ROOT/"data/mlit_2026_all_points.csv"
columns=["longitude","latitude"]+list(fields)
with dest.open("w",encoding="utf-8",newline="") as file:
    w=csv.DictWriter(file,fieldnames=columns,extrasaction="ignore");w.writeheader()
    for f in features:
        geometry=f.get("geometry") or {}
        coord=geometry.get("coordinates") or []
        props=f.get("properties") or {}
        w.writerow({"longitude":coord[0] if len(coord)>=2 else "","latitude":coord[1] if len(coord)>=2 else "",**props})
print(f"Extracted {len(features)} features into {dest}")
