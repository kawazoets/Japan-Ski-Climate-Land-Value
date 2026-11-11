"""Bounded single-prefecture OSM extraction for matrix GitHub Actions."""
import csv,json,os,sys,urllib.parse,urllib.request
from pathlib import Path
PREFS="北海道 青森県 岩手県 宮城県 秋田県 山形県 福島県 茨城県 栃木県 群馬県 埼玉県 千葉県 東京都 神奈川県 新潟県 富山県 石川県 福井県 山梨県 長野県 岐阜県 静岡県 愛知県 三重県 滋賀県 京都府 大阪府 兵庫県 奈良県 和歌山県 鳥取県 島根県 岡山県 広島県 山口県 徳島県 香川県 愛媛県 高知県 福岡県 佐賀県 長崎県 熊本県 大分県 宮崎県 鹿児島県 沖縄県".split()
FIELDS=["osm_type","osm_id","name","prefecture_query","latitude","longitude","landuse","piste_type","sport","source_url","evidence_status"]
def main():
    i=int(sys.argv[1]);pref=PREFS[i];out=Path("parts")/f"pref_{i:02}.csv";out.parent.mkdir(exist_ok=True)
    query=f'[out:json][timeout:75];area["name"="{pref}"]["admin_level"="4"]->.pref;(nwr["landuse"="winter_sports"](area.pref);nwr["piste:type"="downhill"]["name"](area.pref);nwr["sport"="skiing"]["name"](area.pref););out center tags;'
    rows={};status="failed";error=""
    for endpoint in ("https://overpass.kumi.systems/api/interpreter","https://overpass-api.de/api/interpreter"):
        try:
            req=urllib.request.Request(endpoint,data=urllib.parse.urlencode({"data":query}).encode(),headers={"User-Agent":"JapanSkiClimateLandValue/1.0","Content-Type":"application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req,timeout=105) as response:result=json.load(response)
            if "elements" not in result:raise ValueError("No elements field")
            for el in result["elements"]:
                t=el.get("tags") or {};name=t.get("name") or t.get("name:ja") or "";p=el.get("center") or el
                if not name or p.get("lat") is None or p.get("lon") is None:continue
                key=(el.get("type"),el.get("id"))
                rows[key]=dict(osm_type=el.get("type"),osm_id=el.get("id"),name=name,prefecture_query=pref,latitude=p["lat"],longitude=p["lon"],landuse=t.get("landuse",""),piste_type=t.get("piste:type",""),sport=t.get("sport",""),source_url=f"https://www.openstreetmap.org/{el.get('type')}/{el.get('id')}",evidence_status="unverified_osm_geometry")
            status="ok";break
        except Exception as e:error=f"{type(e).__name__}: {str(e)[:130]}"
    with out.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows.values())
    Path("parts") .joinpath(f"status_{i:02}.txt").write_text(f"{pref}\t{status}\t{len(rows)}\t{error}\n",encoding="utf-8")
    print(f"{pref}: {status}, {len(rows)} geometries; {error}",flush=True)
    # Keep partial results and failure evidence even if an endpoint times out.
if __name__=="__main__":main()
