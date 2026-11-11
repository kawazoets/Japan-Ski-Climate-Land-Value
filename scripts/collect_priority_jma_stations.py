"""Greedy nationwide station selection maximizing additional ski-resort coverage.

Selection is based on actual resort-to-JMA station candidate links, not
alphabetical station IDs. Excludes already downloaded station histories.
"""
import csv,collections,sys
from pathlib import Path
from collect_national_jma_snow_history import ROOT
from collect_national_jma_snow_pilot import fetch
import datetime,time
def main():
 index=int(sys.argv[1])
 with (ROOT/"data/jma_historical_block_number_candidates.csv").open(encoding="utf-8-sig",newline="") as f:blocks={r["jma_station_name"]:r for r in csv.DictReader(f)}
 with (ROOT/"data/national_jma_snow_station_candidates.csv").open(encoding="utf-8-sig",newline="") as f:links=list(csv.DictReader(f))
 existing={p.stem for p in (ROOT/"data/jma_station_history").glob("[0-9]*.csv") if not p.stem.endswith("_status")}
 station_resorts=collections.defaultdict(dict);station_meta={}
 for r in links:
  sid=r["jma_station_id"];b=blocks.get(r["jma_station_name"])
  if sid in existing or not b or b["resolution_status"]!="unique_name_match":continue
  d=float(r["straight_line_distance_km"])
  station_resorts[sid][r["candidate_id"]]=min(d,station_resorts[sid].get(r["candidate_id"],float("inf")))
  station_meta[sid]=(r["jma_station_name"],b)
 covered={r["candidate_id"] for r in links if r["jma_station_id"] in existing}
 selected=[]
 for _ in range(min(50,len(station_resorts))):
  def score(sid):
   rs=station_resorts[sid]
   return (sum(d<=20 and cid not in covered for cid,d in rs.items()),sum(d<=10 and cid not in covered for cid,d in rs.items()),sum(cid not in covered for cid in rs),-sum(rs.values())/max(len(rs),1))
  best=max(station_resorts,key=score)
  selected.append(best)
  covered.update(station_resorts[best])
  del station_resorts[best]
 if index>=len(selected):print("No selected station at",index);return
 sid=selected[index];name,b=station_meta[sid]
 rows=[];errors=[]
 for winter in range(2016,2026):
  temp=[]
  try:
   for year,month in [(winter,11),(winter,12),(winter+1,1),(winter+1,2),(winter+1,3),(winter+1,4)]:
    temp.extend([[sid]+x for x in fetch(b["prec_no"],b["block_no"],name,year,month)])
    time.sleep(0.25)
   expected=(datetime.date(winter+1,5,1)-datetime.date(winter,11,1)).days
   if len(temp)!=expected:raise ValueError(f"Expected {expected}, received {len(temp)}")
   rows.extend(temp);print("OK",sid,name,winter,flush=True)
  except Exception as e:
   errors.append(f"{winter}: {e}")
   print("FAIL",sid,name,winter,str(e),flush=True)
 folder=ROOT/"data/jma_priority_station_history";folder.mkdir(parents=True,exist_ok=True)
 with (folder/f"{sid}.csv").open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["station_id","station_name","date","snow_depth_cm","source_url"]);w.writerows(rows)
 with (folder/f"{sid}_status.csv").open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["station_id","station_name","complete_winters","failed_winters","daily_rows","errors"]);w.writerow([sid,name,10-len(errors),len(errors),len(rows)," | ".join(errors)[:1500]])
 print("FINISHED",sid,name,len(rows),len(errors))
if __name__=="__main__":main()
