"""Aggregate verified JMA daily snow-depth observations by winter season.

Winter 2016 = 2016-11-01 through 2017-04-30; the final 2026 winter
is incomplete as of 2026-11-11 and is excluded from complete-season comparisons.
"""
import csv,datetime,collections,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 source=ROOT/"data/jma_daily_snow_depth_2016_2026.csv"
 if not source.exists():raise SystemExit("No real daily JMA observations imported yet")
 with source.open(encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
 required={"station_id","date","snow_depth_cm"}
 if not rows or not required.issubset(rows[0]):raise SystemExit("JMA daily data missing or wrong schema")
 by=collections.defaultdict(dict)
 for r in rows:
  day=datetime.date.fromisoformat(r["date"])
  winter=day.year if day.month>=11 else day.year-1
  if not 2016<=winter<=2025 or day.month not in (11,12,1,2,3,4):continue
  key=(r["station_id"],winter)
  if day in by[key]:raise SystemExit("Duplicate station/date "+str((key,day)))
  value=r["snow_depth_cm"].strip()
  depth=None if not value else float(value)
  if depth is not None and depth<0:raise SystemExit("Negative snow depth")
  by[key][day]=depth
 result=[]
 for (station,winter),daily in sorted(by.items()):
  start=datetime.date(winter,11,1);end=datetime.date(winter+1,4,30)
  expected=(end-start).days+1
  valid=[v for v in daily.values() if v is not None]
  coverage=len(valid)/expected
  result.append([station,winter,expected,len(daily),len(valid),round(coverage,4),sum(v>=1 for v in valid),sum(v>=30 for v in valid),max(valid) if valid else "",round(statistics.mean(valid),2) if valid else "","usable" if coverage>=0.9 else "insufficient_coverage"])
 target=ROOT/"data/jma_snow_winter_season_metrics_2016_2025.csv"
 with target.open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["station_id","winter_start_year","expected_days","rows_present","valid_depth_days","coverage","observed_snow_cover_days_1cm","observed_snow_cover_days_30cm","max_daily_snow_depth_cm","mean_observed_depth_cm","quality_status"]);w.writerows(result)
 print("Winter station-season records",len(result),"usable",sum(x[-1]=="usable" for x in result))
if __name__=="__main__":main()
