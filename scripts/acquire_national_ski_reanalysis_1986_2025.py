"""Acquire ERA5 climate in smaller 10-year chunks, with bounded concurrency and retries."""
import csv,json,time,urllib.parse,urllib.request,collections,datetime,statistics,concurrent.futures,random
from pathlib import Path
P=Path(__file__).resolve().parents[1]
with (P/"data/national_resort_osm_reconciliation.csv").open(encoding="utf-8-sig",newline="") as f: source=list(csv.DictReader(f))
points=[]
for r in source:
 if r["match_status"]!="one_unverified_facility_geometry":continue
 try:points.append((r,float(r["latitude_candidate"]),float(r["longitude_candidate"])))
 except (ValueError,TypeError):pass
assert len(points)>=200
old=P/"data/ski_region_reanalysis_climate_1986_2025.csv"
fields=["candidate_id","resort_name","year","mean_temperature_c","winter_snowfall_cm","days_observed","source","data_type","coordinate_status"]
existing={}
if old.exists():
 with old.open(encoding="utf-8-sig",newline="") as f:
  for r in csv.DictReader(f):
   if r["mean_temperature_c"] and r["winter_snowfall_cm"]:existing[(r["candidate_id"],int(r["year"]))]=r
def fetch(task):
 batch,start,end=task
 params={"latitude":",".join(str(p[1]) for p in batch),"longitude":",".join(str(p[2]) for p in batch),"start_date":f"{start}-01-01","end_date":f"{end}-12-31","daily":"temperature_2m_mean,snowfall_sum","timezone":"Asia/Tokyo","models":"era5"}
 url="https://archive-api.open-meteo.com/v1/archive?"+urllib.parse.urlencode(params)
 error=""
 for attempt in range(5):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"SkiClimateLandValueResearch/1.0"})
   with urllib.request.urlopen(req,timeout=100) as f:payload=json.load(f)
   entries=payload if isinstance(payload,list) else [payload]
   if len(entries)!=len(batch):raise ValueError("Response coordinate mismatch")
   result=[]
   for (r,lat,lon),entry in zip(batch,entries):
    d=entry.get("daily",{});dates=d.get("time",[]);temps=d.get("temperature_2m_mean",[]);snow=d.get("snowfall_sum",[])
    if not (len(dates)==len(temps)==len(snow)):raise ValueError("Daily arrays mismatch")
    years=collections.defaultdict(lambda:{"t":[],"s":[],"days":0})
    for date,t,s in zip(dates,temps,snow):
     day=datetime.date.fromisoformat(date);v=years[day.year];v["days"]+=1
     if t is not None:v["t"].append(float(t))
     if day.month in (1,2,3,4,11,12) and s is not None:v["s"].append(float(s))
    for yr in range(start,end+1):
     v=years[yr]
     if len(v["t"])<300 or len(v["s"])<140:continue
     result.append({"candidate_id":r["candidate_id"],"resort_name":r["resort_name"],"year":yr,"mean_temperature_c":round(statistics.mean(v["t"]),3),"winter_snowfall_cm":round(sum(v["s"]),2),"days_observed":v["days"],"source":"https://open-meteo.com/en/docs/historical-weather-api","data_type":"ERA5 reanalysis estimate; not local station measurement","coordinate_status":"provisional OSM match"})
   return result,None
  except Exception as e:
   error=str(e)
   if attempt<4:time.sleep(min(50,3*(2**attempt))+random.random()*2)
 return [],(batch[0][0]["candidate_id"],start,end,error)
tasks=[]
for i in range(0,len(points),3):
 batch=points[i:i+3]
 for start in (1986,1996,2006,2016):
  end=min(start+9,2025)
  if all((p[0]["candidate_id"],yr) in existing for p in batch for yr in range(start,end+1)):continue
  tasks.append((batch,start,end))
failures=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for rows,err in pool.map(fetch,tasks):
  if err:failures.append(err)
  for r in rows:existing[(r["candidate_id"],int(r["year"]))]=r
outrows=sorted(existing.values(),key=lambda r:(r["candidate_id"],int(r["year"])))
with old.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(outrows)
coverage=collections.Counter(r["candidate_id"] for r in outrows)
complete=sum(n==40 for n in coverage.values())
(P/"reports/ski_region_reanalysis_climate_1986_2025.md").write_text(
 "# Nationwide ski-region historical climate: ERA5 reanalysis\n\n"
 +f"- Resort candidates: {len(points)}\n- Resort-year observations: {len(outrows)}\n- Complete 40-year series: {complete}/{len(points)}\n- Failed 10-year requests: {len(failures)}\n- Failed request details: {failures}\n"
 +"- ERA5 grid estimates, not JMA observations; provisional coordinates and unresolved elevation bias.\n"
 +"- Winter snowfall combines Jan–Apr and Nov–Dec in the same calendar year, not an actual ski season.\n",encoding="utf-8")
print("Complete",complete,"of",len(points),"failures",len(failures))
assert complete>=180,("Coverage below research threshold",complete,len(points),failures[:10])
