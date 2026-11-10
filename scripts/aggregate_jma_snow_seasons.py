"""Aggregate verified daily snow depth into Nov-Apr ski-season indicators.

Input: data/jma_daily_snow_depth.csv (station_id,date,snow_depth_cm,quality_code)
Optional: data/resort_jma_station_mapping.csv (resort_name,station_id,distance_km,verification_status)
No scraping, GitHub Actions, or mail notifications. No missing-as-zero imputation.
"""
import csv,datetime,statistics
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data/jma_daily_snow_depth.csv"
MAPPING=ROOT/"data/resort_jma_station_mapping.csv"
OUTPUT=ROOT/"data/jma_ski_season_snow_metrics.csv"
JOIN=ROOT/"data/resort_snow_metrics.csv"
def season_of(d):
    return d.year+1 if d.month>=11 else d.year
def in_season(d):
    return d.month in (11,12,1,2,3,4)
def main():
    with SOURCE.open(encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
    groups=defaultdict(dict)
    for r in rows:
        d=datetime.date.fromisoformat(r["date"])
        if not in_season(d):continue
        raw=(r.get("snow_depth_cm") or "").strip()
        if not raw:continue
        try:depth=float(raw)
        except ValueError:continue
        if depth<0:continue
        station=r["station_id"].strip()
        if not station:continue
        key=(station,season_of(d))
        if d in groups[key] and groups[key][d]!=depth:
            raise ValueError(f"Conflicting station/day observations: {station}, {d}")
        groups[key][d]=depth
    out=[]
    for (station,year),days in sorted(groups.items()):
        start=datetime.date(year-1,11,1);end=datetime.date(year,4,30)
        total=(end-start).days+1
        observed=len(days)
        out.append({"station_id":station,"season_end_year":year,"season_start":start.isoformat(),"season_end":end.isoformat(),"expected_days":total,"observed_days":observed,"coverage_ratio":round(observed/total,4),"days_snow_ge_10cm_observed":sum(x>=10 for x in days.values()),"days_snow_ge_30cm_observed":sum(x>=30 for x in days.values()),"max_snow_depth_cm":max(days.values()),"snow_depth_median_cm":round(statistics.median(days.values()),2),"metric_status":"usable" if observed/total>=0.9 else "insufficient_coverage"})
    OUTPUT.parent.mkdir(exist_ok=True)
    fields=["station_id","season_end_year","season_start","season_end","expected_days","observed_days","coverage_ratio","days_snow_ge_10cm_observed","days_snow_ge_30cm_observed","max_snow_depth_cm","snow_depth_median_cm","metric_status"]
    with OUTPUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    if MAPPING.exists():
        with MAPPING.open(encoding="utf-8-sig",newline="") as f:mappings=list(csv.DictReader(f))
        by_station=defaultdict(list)
        for r in out:by_station[r["station_id"]].append(r)
        joined=[]
        for m in mappings:
            if m.get("verification_status")!="verified":continue
            for r in by_station.get(m["station_id"],[]):
                joined.append({"resort_name":m["resort_name"],"station_id":m["station_id"],"station_distance_km":m.get("distance_km",""),**r})
        with JOIN.open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=["resort_name","station_id","station_distance_km"]+fields[1:]);w.writeheader();w.writerows(joined)
        print(f"Saved {len(joined)} resort-season rows")
    print(f"Saved {len(out)} station-season rows; usable={sum(r['metric_status']=='usable' for r in out)}")
if __name__=="__main__":main()
