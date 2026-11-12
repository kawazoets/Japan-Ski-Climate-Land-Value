"""Acquire historical gridded ERA5 climate estimates for nationwide ski regions.
Open-Meteo Historical API; reanalysis/model data, NOT JMA station observations.
Annual mean temperature and winter (Nov-Apr) snowfall from 1986-2025.
"""
import csv,json,time,urllib.parse,urllib.request,collections,datetime,statistics
from pathlib import Path
P=Path(__file__).resolve().parents[1]
with (P/"data/national_resort_osm_reconciliation.csv").open(encoding="utf-8-sig",newline="") as f:rs=list(csv.DictReader(f))
points=[]
for r in rs:
 if r["match_status"]!="one_unverified_facility_geometry":continue
 try:lat=float(r["latitude_candidate"]);lon=float(r["longitude_candidate"])
 except (ValueError,TypeError):continue
 points.append((r,lat,lon))
assert len(points)>100,("Too few coordinates",len(points))
# Pilot a small sample before attempting nationwide requests.
points=points[:10]
out=P/"data/ski_region_reanalysis_climate_1986_2025.csv"
fields=["candidate_id","resort_name","year","mean_temperature_c","winter_snowfall_cm","days_observed","source","data_type","coordinate_status"]
rows=[];failures=[]
for index in range(0,len(points),2):
 batch=points[index:index+2]
 params={"latitude":",".join(str(x[1]) for x in batch),"longitude":",".join(str(x[2]) for x in batch),"start_date":"1986-01-01","end_date":"2025-12-31","daily":"temperature_2m_mean,snowfall_sum","timezone":"Asia/Tokyo","models":"era5"}
 url="https://archive-api.open-meteo.com/v1/archive?"+urllib.parse.urlencode(params)
 payload=None
 for attempt in range(2):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"ClimateLandValueResearch/1.0 academic analysis"})
   with urllib.request.urlopen(req,timeout=55) as f:payload=json.load(f)
   break
  except Exception as e:
   if attempt==1:failures.append((index,str(e)))
   else:time.sleep(3*(attempt+1))
 if payload is None:continue
 entries=payload if isinstance(payload,list) else [payload]
 if len(entries)!=len(batch):
  failures.append((index,"Response coordinate count mismatch"));continue
 for (r,lat,lon),entry in zip(batch,entries):
  daily=entry.get("daily",{})
  dates=daily.get("time",[]);temps=daily.get("temperature_2m_mean",[]);snow=daily.get("snowfall_sum",[])
  if not(len(dates)==len(temps)==len(snow)):
   failures.append((r["candidate_id"],"Daily series lengths mismatch"));continue
  by_year=collections.defaultdict(lambda:{"temp":[],"snow":[],"days":0})
  for date,temp,snowfall in zip(dates,temps,snow):
   d=datetime.date.fromisoformat(date);yr=d.year
   if temp is not None:by_year[yr]["temp"].append(float(temp))
   if d.month in (11,12,1,2,3,4) and snowfall is not None:by_year[yr]["snow"].append(float(snowfall))
   by_year[yr]["days"]+=1
  for yr in range(1986,2026):
   d=by_year[yr]
   rows.append({"candidate_id":r["candidate_id"],"resort_name":r["resort_name"],"year":yr,"mean_temperature_c":round(statistics.mean(d["temp"]),3) if len(d["temp"])>=300 else "","winter_snowfall_cm":round(sum(d["snow"]),2) if len(d["snow"])>=140 else "","days_observed":d["days"],"source":"https://open-meteo.com/en/docs/historical-weather-api","data_type":"ERA5 reanalysis estimate; not local station measurement","coordinate_status":"provisional OSM match"})
 time.sleep(2)
with out.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
coverage=collections.Counter(int(r["year"]) for r in rows if r["mean_temperature_c"]!="")
report=P/"reports/ski_region_reanalysis_climate_1986_2025.md"
report.write_text("# Pilot ski-region historical climate: ERA5 reanalysis\n\n"+
 f"- Resort candidates with provisional coordinates: {len(points)}\n- Resort-year rows: {len(rows)}\n- Years with >=100 candidate temperatures: {sum(coverage[y]>=100 for y in range(1986,2026))}/40\n- Failed batches: {failures}\n"+
 "- Source: Open-Meteo Historical API, ERA5 gridded reanalysis; **not official JMA observed weather**.\n"+
 "- Annual temperatures are calendar-year means. Snowfall is summed over Jan-Apr and Nov-Dec of each calendar year, not a single ski winter; do not interpret as a resort's operating season.\n"+
 "- Resort coordinates are provisional; ERA5 spatial resolution does not resolve mountain slopes or elevation accurately. No causal conclusion about land prices follows from this dataset alone.\n",encoding="utf-8")
assert len(rows)>=5*40,("Pilot climate acquisition failed",len(rows),failures)
print("Climate rows",len(rows),"failed batches",len(failures))
