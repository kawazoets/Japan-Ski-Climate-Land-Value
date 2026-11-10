"""Collect OSM ski-area location candidates for Japan (not verified resort entrances).

Queries only site=piste relations and named winter_sports areas. A returned
representative center is NOT necessarily the resort entrance or ski base.
"""
import csv,json,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data/osm_resort_geocandidates.csv"
QUERY='''[out:json][timeout:180];
area["ISO3166-1"="JP"]["admin_level"="2"]->.japan;
(
  nwr["site"="piste"]["name"](area.japan);
  nwr["landuse"="winter_sports"]["name"](area.japan);
  nwr["sport"="skiing"]["name"](area.japan);
);
out center tags;'''
ENDPOINTS=["https://overpass.kumi.systems/api/interpreter","https://overpass-api.de/api/interpreter"]
def fetch():
    errors=[]
    for endpoint in ENDPOINTS:
        try:
            data=urllib.parse.urlencode({"data":QUERY}).encode()
            req=urllib.request.Request(endpoint,data=data,headers={"User-Agent":"JapanSkiClimateLandValue/1.0 (noncommercial research)"})
            with urllib.request.urlopen(req,timeout=220) as resp:
                obj=json.load(resp)
            if "elements" not in obj:raise RuntimeError("Missing elements")
            return endpoint,obj["elements"]
        except Exception as e:errors.append(f"{endpoint}: {e}")
    raise RuntimeError("OSM fetch failed: "+"; ".join(errors))
def main():
    endpoint,elements=fetch()
    rows=[]
    for e in elements:
        tags=e.get("tags") or {}
        center=e.get("center") or e
        if "lat" not in center or "lon" not in center:continue
        name=tags.get("name") or ""
        if not name:continue
        rows.append({"osm_type":e["type"],"osm_id":e["id"],"name":name,"name_en":tags.get("name:en",""),"latitude":center["lat"],"longitude":center["lon"],"feature_type":tags.get("site") or tags.get("landuse") or tags.get("sport"),"source_url":f'https://www.openstreetmap.org/{e["type"]}/{e["id"]}',"coordinate_status":"osm_representative_center_unverified","retrieval_endpoint":endpoint})
    if not rows:raise SystemExit("No named OSM features returned")
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f"Saved {len(rows)} unverified OSM location candidates to {OUT}")
if __name__=="__main__":main()
