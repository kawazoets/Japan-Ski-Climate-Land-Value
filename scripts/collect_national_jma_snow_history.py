"""Extend verified nationwide JMA snow stations across ten complete winters.

Use only station links with successful 2024 winter pilot; never extrapolate
failed or ambiguous mappings. Process a bounded batch for GitHub Actions.
"""
import csv,datetime,sys,time
from pathlib import Path
from collect_national_jma_snow_pilot import fetch,ROOT
def main():
 batch=int(sys.argv[1]) if len(sys.argv)>1 else 0
 with (ROOT/"data/jma_nationwide_snow_pilot_collection_status.csv").open(encoding="utf-8",newline="") as f:success=[r for r in csv.DictReader(f) if r["status"]=="collected"]
 with (ROOT/"data/jma_historical_block_number_candidates.csv").open(encoding="utf-8",newline="") as f:blocks={r["jma_station_name"]:r for r in csv.DictReader(f)}
 stations=success[batch*3:(batch+1)*3]
 if not stations:raise SystemExit("No verified stations in batch")
 out=ROOT/f"data/jma_national_snow_history_batch_{batch:02d}.csv"
 status=ROOT/f"data/jma_national_snow_history_batch_{batch:02d}_status.csv"
 rows=[];results=[]
 for st in stations:
  sid,name=st["station_id"],st["station_name"];b=blocks[name]
  allrows=[];failed=[]
  for winter in range(2016,2026):
   winterrows=[]
   try:
    for year,month in [(winter,11),(winter,12),(winter+1,1),(winter+1,2),(winter+1,3),(winter+1,4)]:
     for record in fetch(b["prec_no"],b["block_no"],name,year,month):
      winterrows.append([sid]+record)
     time.sleep(0.45)
    expected=(datetime.date(winter+1,5,1)-datetime.date(winter,11,1)).days
    if len(winterrows)!=expected:raise ValueError(f"Expected {expected} daily rows, got {len(winterrows)}")
    allrows.extend(winterrows)
    print("OK",sid,name,winter,len(winterrows),flush=True)
   except Exception as e:
    failed.append(f"{winter}: {type(e).__name__}: {e}")
    print("FAILED",sid,name,winter,str(e),flush=True)
  rows.extend(allrows)
  results.append([sid,name,len(allrows),10-len(failed),len(failed)," | ".join(failed)[:900]])
 with out.open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["station_id","station_name","date","snow_depth_cm","source_url"]);w.writerows(rows)
 with status.open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["station_id","station_name","daily_rows","complete_winters","failed_winters","errors"]);w.writerows(results)
 print("Batch",batch,"stations",len(stations),"rows",len(rows))
if __name__=="__main__":main()
