"""Match every ski resort with geocoded candidate location to official JMA snow stations.

Source: https://www.jma.go.jp/jma/kishou/know/amedas/snow_master.zip
Distances are horizontal and cannot establish representativeness for mountain snow.
"""
import csv,io,zipfile,urllib.request,math,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL="https://www.jma.go.jp/jma/kishou/know/amedas/snow_master.zip"
def dist(lat1,lon1,lat2,lon2):
 a,b=math.radians(lat1),math.radians(lat2)
 h=math.sin((b-a)/2)**2+math.cos(a)*math.cos(b)*math.sin(math.radians(lon2-lon1)/2)**2
 return 12742*math.asin(min(1,math.sqrt(h)))
def main():
 with urllib.request.urlopen(urllib.request.Request(URL,headers={"User-Agent":"Japan-Ski-Climate-Land-Value/1.0"}),timeout=60) as r:raw=r.read()
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  name=next((n for n in z.namelist() if n.lower().endswith(".csv")),None)
  if not name:raise SystemExit("Official master CSV missing")
  stations=list(csv.DictReader(io.StringIO(z.read(name).decode("cp932"))))
 required={"観測所番号","観測所名","緯度(度)","緯度(分)","経度(度)","経度(分)","海面上の高さ(ｍ)","種類"}
 if not stations or not required.issubset(stations[0]):raise SystemExit("JMA station schema mismatch")
 cleaned=[]
 for s in stations:
  try:
   lat=float(s["緯度(度)"])+float(s["緯度(分)"])/60
   lon=float(s["経度(度)"])+float(s["経度(分)"])/60
   if not (20<lat<47 and 122<lon<154):continue
   cleaned.append((s,lat,lon))
  except (ValueError,TypeError):continue
 if len(cleaned)<250:raise SystemExit("Too few valid official stations: "+str(len(cleaned)))
 with (ROOT/"data/national_resort_osm_reconciliation.csv").open(encoding="utf-8-sig",newline="") as f:resorts=list(csv.DictReader(f))
 if len(resorts)!=451:raise SystemExit("Unexpected resort cohort size")
 columns=["candidate_id","resort_name","prefecture","coordinate_status","station_rank","jma_station_id","jma_station_name","jma_region","jma_type","jma_station_latitude","jma_station_longitude","jma_station_altitude_m","straight_line_distance_km","snow_observation_status","source_url"]
 result=[]
 for r in resorts:
  try:lat=float(r["latitude_candidate"]);lon=float(r["longitude_candidate"])
  except (ValueError,TypeError):continue
  candidates=sorted(((dist(lat,lon,slat,slon),s,slat,slon) for s,slat,slon in cleaned),key=lambda x:x[0])
  for rank,(d,s,slat,slon) in enumerate(candidates[:5],1):
   result.append([r["candidate_id"],r["resort_name"],r["prefecture"],r["match_status"],rank,s["観測所番号"],s["観測所名"],s["都府県振興局"],s["種類"],round(slat,6),round(slon,6),s["海面上の高さ(ｍ)"],round(d,3),"not_yet_collected",URL])
 target=ROOT/"data/national_jma_snow_station_candidates.csv"
 with target.open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(columns);w.writerows(result)
 first=[r for r in result if r[4]==1]
 nearest5=sum(r[12]<=5 for r in first)
 nearest10=sum(r[12]<=10 for r in first)
 nearest20=sum(r[12]<=20 for r in first)
 report=ROOT/"reports/national_jma_snow_station_matching.md"
 report.write_text(f"""# JMA snow observation station proximity inventory

- Official JMA snow station master: `{name}`, {len(stations)} rows; {len(cleaned)} with valid coordinates.
- Ski resort candidates: {len(resorts)}.
- Resorts with provisional OSM coordinates: {len(first)}.
- Five nearest official JMA snow stations each: {len(result)} candidate links.
- Nearest JMA snow station within 5 km: {nearest5}.
- Within 10 km: {nearest10}.
- Within 20 km: {nearest20}.
- Actual daily snow observations imported: **0**.

This is a station-proximity inventory, **not** a validated snow-depth time series.
Station elevation is recorded but ski resort elevation is not yet verified.
Mountain snow cover can differ substantially from valley stations; the nearest
station is not automatically suitable. Missing resort coordinates remain missing.
Official source: {URL}
""",encoding="utf-8")
 print(report.read_text())
if __name__=="__main__":main()
