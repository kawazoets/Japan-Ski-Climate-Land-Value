"""Fetch ski-area OSM geometry by prefecture using bounded Overpass queries.

One request per prefecture, limited to winter-sports landuse or named ski
downhill pistes. Save partial results even if an endpoint fails; fail clearly
when no useful data is returned. No recurring schedule.
"""
import csv,json,time,urllib.parse,urllib.request,collections,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data/national_ski_resort_candidate_master.csv"
OUT=ROOT/"data/osm_national_ski_area_geometries.csv"
AUDIT=ROOT/"reports/osm_national_geocoding_harvest.md"
ENDPOINTS=("https://overpass.kumi.systems/api/interpreter","https://overpass-api.de/api/interpreter")
def main():
    with MASTER.open(encoding="utf-8-sig",newline="") as f:master=list(csv.DictReader(f))
    # JIS prefecture names from directory region heading; strip trailing counts.
    prefectures=sorted({re.sub(r"\\d.*$", "", r["region_raw"].strip()) for r in master if r.get("region_raw")})
    if len(prefectures)<20:raise SystemExit(f"Insufficient prefecture coverage: {len(prefectures)}")\n    print(f"Validated prefecture names ({len(prefectures)}): {prefectures}",flush=True)
    records={};failures=[]
    for i,pref in enumerate(prefectures,1):
        query=f'''[out:json][timeout:90];area["name"="{pref}"]["admin_level"="4"]->.pref;(nwr["landuse"="winter_sports"](area.pref);nwr["piste:type"="downhill"]["name"](area.pref);nwr["sport"="skiing"]["name"](area.pref););out center tags;'''
        success=False
        for endpoint in ENDPOINTS:
            try:
                payload=urllib.parse.urlencode({"data":query}).encode()
                req=urllib.request.Request(endpoint,data=payload,headers={"User-Agent":"JapanSkiClimateLandValue/1.0 (academic, bounded prefecture query)","Content-Type":"application/x-www-form-urlencoded"})
                with urllib.request.urlopen(req,timeout=125) as response:result=json.load(response)
                if "elements" not in result:raise ValueError("Missing elements")
                for el in result["elements"]:
                    tags=el.get("tags") or {};name=tags.get("name") or tags.get("name:ja") or ""
                    point=el.get("center") or el
                    lat=point.get("lat");lon=point.get("lon")
                    if not name or lat is None or lon is None:continue
                    key=(el.get("type"),el.get("id"))
                    records[key]={"osm_type":el.get("type"),"osm_id":el.get("id"),"name":name,"prefecture_query":pref,"latitude":lat,"longitude":lon,"landuse":tags.get("landuse",""),"piste_type":tags.get("piste:type",""),"sport":tags.get("sport",""),"source_url":f"https://www.openstreetmap.org/{el.get('type')}/{el.get('id')}","evidence_status":"unverified_osm_geometry"}
                success=True;break
            except Exception as exc:
                failures.append(f"{pref} {endpoint}: {type(exc).__name__}: {str(exc)[:110]}")
        print(f"[{i}/{len(prefectures)}] {pref}: {'ok' if success else 'failed'}; geometries={len(records)}",flush=True)
        time.sleep(2)
    if not records:raise SystemExit("No OSM geometries obtained; see network/Overpass availability")
    OUT.parent.mkdir(exist_ok=True)
    fields=["osm_type","osm_id","name","prefecture_query","latitude","longitude","landuse","piste_type","sport","source_url","evidence_status"]
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(sorted(records.values(),key=lambda r:(r["prefecture_query"],r["name"],str(r["osm_id"]))))
    AUDIT.parent.mkdir(exist_ok=True)
    AUDIT.write_text("# Nationwide OSM ski-area harvest\n\n"+f"- Prefecture queries: {len(prefectures)}\n- Distinct named OSM features: {len(records)}\n- Failed endpoint attempts: {len(failures)}\n\n"+ "## Errors (if any)\n"+("\n".join("- "+x for x in failures[:100]) or "None")+"\n\nThese are unverified OSM features, not an official list of operating resorts. Pistes can produce multiple geometries per resort. No source records are deleted.\n",encoding="utf-8")
if __name__=="__main__":main()
