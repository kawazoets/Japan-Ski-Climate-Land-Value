"""Collect all unambiguous JMA snow stations linked to the national resort cohort.

One station per matrix job, ten complete winters, with resumable artifacts.
The 2024-25 pilot is not reused as evidence of full-period coverage.
"""
import csv,datetime,sys,time,random
from pathlib import Path
from collect_national_jma_snow_pilot import fetch,ROOT
def main():
 index=int(sys.argv[1])
 with (ROOT/"data/jma_historical_block_number_candidates.csv").open(encoding="utf-8-sig",newline="") as f:
  blocks={r["jma_station_name"]:r for r in csv.DictReader(f)}
 with (ROOT/"data/national_jma_snow_station_candidates.csv").open(encoding="utf-8-sig",newline="") as f:
  links=list(csv.DictReader(f))
 stations={}
 for r in links:
  b=blocks.get(r["jma_station_name"])
  if b and b["resolution_status"]=="unique_name_match":
   stations[r["jma_station_id"]]=(r["jma_station_name"],b)
 selected=sorted(stations.items(),key=lambda item:int(item[0]))
 if index>=len(selected):
  print("No station at index",index,"out of",len(selected));return
 sid,(name,b)=selected[index]
 rows=[];failures=[]
 for winter in range(2016,2026):
  winterrows=[]
  try:
   for year,month in [(winter,11),(winter,12),(winter+1,1),(winter+1,2),(winter+1,3),(winter+1,4)]:
    monthly=fetch(b["prec_no"],b["block_no"],name,year,month)
    winterrows.extend([[sid]+r for r in monthly])
    time.sleep(0.25)
   expected=(datetime.date(winter+1,5,1)-datetime.date(winter,11,1)).days
   if len(winterrows)!=expected:raise ValueError(f"Expected {expected}, received {len(winterrows)}")
   rows.extend(winterrows)
   print("OK",sid,name,winter,len(winterrows),flush=True)
  except Exception as e:
   failures.append(f"{winter}: {type(e).__name__}: {e}")
   print("FAIL",sid,name,winter,str(e),flush=True)
 dest=ROOT/"data"/"jma_station_history"
 dest.mkdir(parents=True,exist_ok=True)
 with (dest/f"{sid}.csv").open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["station_id","station_name","date","snow_depth_cm","source_url"]);w.writerows(rows)
 with (dest/f"{sid}_status.csv").open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["station_id","station_name","complete_winters","failed_winters","daily_rows","errors"]);w.writerow([sid,name,10-len(failures),len(failures),len(rows)," | ".join(failures)[:1000]])
 print("RESULT",sid,name,"rows",len(rows),"failures",len(failures),flush=True)
if __name__=="__main__":main()
