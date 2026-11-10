"""Match a local OSM ski-area extract against directory candidates.

Input OSM GeoJSON can be downloaded from a regional Geofabrik extract or
generated using osmium. This script makes no network requests and does not
start GitHub Actions. It preserves the OSM object ID and source.
"""
import csv,json,re,sys,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def normalize(s):
    s=unicodedata.normalize("NFKC",str(s)).lower()
    s=re.sub(r"[\s・･‐－-]+","",s)
    return s
def main(path):
    with (ROOT/"data/directory_classified.csv").open(encoding="utf-8",newline="") as f:
        directory=[r for r in csv.DictReader(f) if r["candidate_class"] in ("operating_unverified","possibly_closed")]
    index={}
    for r in directory:index.setdefault(normalize(r["resort_name"]),[]).append(r)
    with open(path,encoding="utf-8") as f:obj=json.load(f)
    rows=[];seen=set()
    for feature in obj.get("features",[]):
        p=feature.get("properties") or {}
        if not any((p.get("site")=="piste",p.get("landuse")=="winter_sports",p.get("sport")=="skiing")):continue
        name=p.get("name")
        if not name:continue
        geometry=feature.get("geometry") or {}
        coords=geometry.get("coordinates")
        if geometry.get("type")!="Point" or not isinstance(coords,list) or len(coords)<2:continue
        for r in index.get(normalize(name),[]):
            key=(r["resort_name"],p.get("@id",feature.get("id",name)))
            if key in seen:continue
            seen.add(key)
            rows.append({"directory_name":r["resort_name"],"osm_name":name,"latitude":coords[1],"longitude":coords[0],"osm_id":p.get("@id",feature.get("id","")),"source":"local_osm_geojson","match_status":"exact_normalized_name_only","coordinate_status":"osm_point_not_verified_entrance","directory_class":r["candidate_class"]})
    out=ROOT/"data/osm_local_name_matches.csv"
    with out.open("w",encoding="utf-8",newline="") as f:
        fields=["directory_name","osm_name","latitude","longitude","osm_id","source","match_status","coordinate_status","directory_class"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    print(f"{len(rows)} name matches; wrote {out}")
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("Usage: python scripts/match_local_osm_geojson.py path/to/osm_points.geojson")
    main(sys.argv[1])
