"""Collect candidate ski areas from OpenStreetMap Overpass; NOT the authoritative 417-resort roster."""
import csv, json, urllib.parse, urllib.request
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
QUERY='''[out:json][timeout:180];area["ISO3166-1"="JP"][admin_level=2]->.jp;(nwr["landuse"="winter_sports"](area.jp);nwr["piste:type"="downhill"](area.jp);nwr["sport"="skiing"](area.jp);nwr["aerialway"="station"](area.jp););out center tags;'''
ENDPOINTS=["https://overpass.kumi.systems/api/interpreter","https://overpass-api.de/api/interpreter"]
def fetch():
    for endpoint in ENDPOINTS:
        try:
            req=urllib.request.Request(endpoint,data=urllib.parse.urlencode({"data":QUERY}).encode(),headers={"User-Agent":"JapanSkiClimateLandValueResearch/0.1","Content-Type":"application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req,timeout=230) as r:return json.load(r),endpoint
        except Exception as exc: print(f"{endpoint}: {exc}")
    raise RuntimeError("All Overpass endpoints failed; preserve existing data.")
def main():
    data,endpoint=fetch()
    rows=[]
    for e in data.get("elements",[]):
        tags=e.get("tags",{})
        if not tags.get("name") and not tags.get("name:ja"):continue
        center=e.get("center",e)
        lat,lon=center.get("lat"),center.get("lon")
        if lat is None or lon is None:continue
        rows.append([f'{e["type"]}/{e["id"]}',tags.get("name:ja") or tags.get("name"),lat,lon,tags.get("landuse",""),tags.get("piste:type",""),tags.get("sport",""),tags.get("aerialway",""),f'https://www.openstreetmap.org/{e["type"]}/{e["id"]}',endpoint,datetime.now(timezone.utc).isoformat()])
    path=ROOT/"data"/"osm_ski_candidates.csv"
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f);w.writerow(["osm_id","name","latitude","longitude","landuse","piste_type","sport","aerialway","source_url","overpass_endpoint","collected_at_utc"]);w.writerows(sorted(rows,key=lambda r:r[0]))
    print(f"Saved {len(rows)} raw candidates. Duplicates and non-resort objects are expected.")
if __name__=="__main__":main()
