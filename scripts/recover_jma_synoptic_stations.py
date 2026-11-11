"""Retry 15 failed synoptic stations with verified daily_s1 snow column."""
import csv,sys,datetime,time
from pathlib import Path
from collect_national_jma_snow_pilot import ROOT,fetch
def main():
 index=int(sys.argv[1])
 folders=[ROOT/"data/jma_station_history",ROOT/"data/jma_priority_station_history"]
 failed={}
 for folder in folders:
  for p in folder.glob("*_status.csv"):
   with p.open(encoding="utf-8-sig",newline="") as f:
    for r in csv.DictReader(f):
     if int(r["complete_winters"])==0:failed[r["station_id"]]=r["station_name"]
 with (ROOT/"data/jma_historical_block_number_candidates.csv").open(encoding="utf-8-sig",newline="") as f:blocks={r["jma_station_name"]:r for r in csv.DictReader(f)}
 selected=sorted(failed.items(),key=lambda v:int(v[0]))
 if index>=len(selected):return
 sid,name=selected[index];b=blocks[name]
 rows=[];errors=[]
 for winter in range(2016,2026):
  partial=[]
  try:
   for year,month in [(winter,11),(winter,12),(winter+1,1),(winter+1,2),(winter+1,3),(winter+1,4)]:
    partial.extend([[sid]+r for r in fetch(b["prec_no"],b["block_no"],name,year,month)])
    time.sleep(0.3)
   expected=(datetime.date(winter+1,5,1)-datetime.date(winter,11,1)).days
   if len(partial)!=expected:raise ValueError(f"Expected {expected} rows, got {len(partial)}")
   rows.extend(partial);print("OK",sid,name,winter,flush=True)
  except Exception as e:errors.append(f"{winter}: {type(e).__name__}: {e}");print("FAIL",sid,name,winter,str(e),flush=True)
 folder=ROOT/"data/jma_synoptic_station_history";folder.mkdir(parents=True,exist_ok=True)
 with (folder/f"{sid}.csv").open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["station_id","station_name","date","snow_depth_cm","source_url"]);w.writerows(rows)
 with (folder/f"{sid}_status.csv").open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["station_id","station_name","complete_winters","failed_winters","daily_rows","errors"]);w.writerow([sid,name,10-len(errors),len(errors),len(rows)," | ".join(errors)[:1200]])
 print("RESULT",sid,name,len(rows),"days",len(errors),"failed winters",flush=True)
if __name__=="__main__":main()
