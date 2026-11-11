"""Link the real 2016-2026 MLIT point-year panel to all geocoded ski-area candidates.

Input: data/MLIT_land_prices_2016_2026.csv (derived from official 2026 L01 archive)
No extrapolation; compare only identical point IDs observed in both endpoint years.
A point can fall within several resort buffers; retain all memberships with explicit IDs.
"""
import csv,math,collections,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RADII=(3,5,10,20)
def read(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def km(a,b,c,d):
 p1,p2=math.radians(a),math.radians(c)
 dp=p2-p1;dl=math.radians(d-b)
 x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
 return 12742*math.asin(min(1,math.sqrt(x)))
def main():
 source=ROOT/"data/MLIT_land_prices_2016_2026.csv"
 if not source.exists():raise SystemExit("Real extracted MLIT panel missing: data/MLIT_land_prices_2016_2026.csv")
 resorts=read(ROOT/"data/national_resort_osm_reconciliation.csv")
 places=[r for r in resorts if r["match_status"]=="one_unverified_facility_geometry" and r["latitude_candidate"] and r["longitude_candidate"]]
 records=read(source)
 by_point=collections.defaultdict(dict);details={}
 for r in records:
  pid=r["point_id_2026"];year=int(r["year"]);price=float(r["price_jpy_per_sqm"])
  if price<=0:raise SystemExit("Nonpositive price")
  if year in by_point[pid]:raise SystemExit("Duplicate point-year "+pid+":"+str(year))
  by_point[pid][year]=price
  details[pid]=r
 # Only 2026 observation points: earlier delisted sites are not represented.
 eligible=[(pid,p) for pid,p in by_point.items() if 2016 in p and 2026 in p]
 stats=collections.defaultdict(list); counts=collections.Counter();joined=[]
 for pid,prices in eligible:
  point=details[pid];a=float(point["latitude"]);b=float(point["longitude"])
  change=(prices[2026]/prices[2016]-1)*100
  for ski in places:
   slat=float(ski["latitude_candidate"]);slon=float(ski["longitude_candidate"])
   if abs(a-slat)>0.2 or abs(b-slon)>0.35:continue
   distance=km(a,b,slat,slon)
   if distance>20:continue
   for radius in RADII:
    if distance<=radius:
     key=(ski["candidate_id"],radius)
     stats[key].append(change);counts[key]+=1
   joined.append([ski["candidate_id"],ski["resort_name"],ski["prefecture"],pid,round(distance,3),point["municipality_code"],point["land_use_2026"],int(prices[2016]),int(prices[2026]),round(change,3),"unverified_osm_geometry"])
 out=ROOT/"data/ski_resort_mlit_point_pairs_2016_2026.csv"
 with out.open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["candidate_id","resort_name","prefecture","point_id_2026","distance_km","municipality_code","land_use_2026","price_2016","price_2026","change_pct","coordinate_quality"]);w.writerows(joined)
 summary=[]
 for ski in resorts:
  for radius in RADII:
   values=stats.get((ski["candidate_id"],radius),[])
   summary.append([ski["candidate_id"],ski["resort_name"],ski["prefecture"],ski["match_status"],radius,len(values),round(statistics.median(values),3) if values else "",round(statistics.mean(values),3) if values else "","2026_survivor_points_only"])
 target=ROOT/"data/ski_resort_mlit_buffer_summary_2016_2026.csv"
 with target.open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["candidate_id","resort_name","prefecture","coordinate_status","radius_km","matched_same_points_2016_2026","median_change_pct","mean_change_pct","sampling_limitation"]);w.writerows(summary)
 report=ROOT/"reports/ski_resort_land_price_full_cohort.md"
 report.write_text(f"""# Nationwide ski-resort × MLIT 2016–2026 land-price linkage

- Candidate resorts retained (including closed/paused): **{len(resorts)}**
- Candidate resorts with one provisional OSM geometry: **{len(places)}**
- Official MLIT 2026 point IDs in input: **{len(by_point)}**
- Identical point IDs with both 2016 and 2026 prices: **{len(eligible)}**
- Resort–point pairs within 20 km: **{len(joined)}**
- Resort/radius rows (including explicit no-data cases): **{len(summary)}**

This is a descriptive geographic buffer analysis, not a causal estimate. Each
ski resort location is an unverified OSM geometry. Nearby resorts can share
the same land-price point, so observations are not independent. Only land-price
points retained in the 2026 dataset are represented; historical point closures
and changes of sampling frame create survivor bias. A 2026 coordinate is used
for all years, so relocations or land-use changes are not corrected. The
geographic buffer does not identify ski-related parcels or tourism exposure.
Missing geocodes and empty buffers remain explicit missing cases.
""",encoding="utf-8")
 print(report.read_text(encoding="utf-8"))
if __name__=="__main__":main()
