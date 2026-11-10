"""Collect ski-area OSM candidates using small bounded regional requests.

Avoid expensive whole-Japan Overpass area queries. Partial results are saved
with explicit coverage status; they are not a verified ski-resort census.
"""
import csv,json,urllib.parse,urllib.request,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data/osm_resort_geocandidates.csv"
STATUS=ROOT/"reports/osm_geocandidate_collection_status.json"
# Bounding boxes are geographic query windows, not administrative prefectures.
REGIONS={
 "hokkaido_west":(41.3,139.2,44.2,142.1),
 "hokkaido_east":(42.4,141.8,45.6,145.9),
 "tohoku_north":(39.5,139.3,41.6,142.3),
 "tohoku_south":(37.5,139.1,39.6,141.8),
 "kanto":(35.0,138.0,37.7,140.8),
 "nagano_niigata":(35.4,137.4,38.6,139.8),
 "hokuriku_chubu":(34.6,135.5,37.4,138.4),
 "west_japan":(31.0,129.0,36.1,136.4),
}
ENDPOINTS=["https://overpass.kumi.systems/api/interpreter","https://overpass-api.de/api/interpreter"]
def request_region(bbox):
    bb=",".join(map(str,bbox))
    query=f'[out:json][timeout:45];(nwr["site"="piste"]["name"]({bb});nwr["landuse"="winter_sports"]["name"]({bb}););out center tags;'
    errors=[]
    for endpoint in ENDPOINTS:
        try:
            data=urllib.parse.urlencode({"data":query}).encode()
            req=urllib.request.Request(endpoint,data=data,headers={"User-Agent":"JapanSkiClimateLandValue/1.0","Content-Type":"application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req,timeout=65) as response:obj=json.load(response)
            if "elements" not in obj:raise ValueError("Missing elements")
            return obj["elements"],endpoint,None
        except Exception as exc:errors.append(str(exc)[:180])
    return [],None,"; ".join(errors)
def main():
    rows={};coverage={}
    for name,bbox in REGIONS.items():
        elements,endpoint,error=request_region(bbox)
        coverage[name]={"status":"ok" if endpoint else "failed","elements":len(elements),"endpoint":endpoint,"error":error}
        print(name,coverage[name],flush=True)
        for e in elements:
            tags=e.get("tags") or {};c=e.get("center") or e
            if not tags.get("name") or "lat" not in c or "lon" not in c:continue
            key=(e["type"],e["id"])
            rows[key]={"osm_type":e["type"],"osm_id":e["id"],"name":tags["name"],"name_en":tags.get("name:en",""),"latitude":c["lat"],"longitude":c["lon"],"feature_type":tags.get("site") or tags.get("landuse") or "","source_url":f'https://www.openstreetmap.org/{e["type"]}/{e["id"]}',"coordinate_status":"osm_representative_center_unverified","retrieval_endpoint":endpoint}
        time.sleep(1)
    STATUS.parent.mkdir(exist_ok=True)
    STATUS.write_text(json.dumps({"coverage":coverage,"candidate_count":len(rows)},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if not rows:raise SystemExit("No coordinate candidates; see status report")
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(next(iter(rows.values()))));w.writeheader();w.writerows(rows.values())
    print(f"Saved {len(rows)} candidates; incomplete regions remain flagged")
if __name__=="__main__":main()
