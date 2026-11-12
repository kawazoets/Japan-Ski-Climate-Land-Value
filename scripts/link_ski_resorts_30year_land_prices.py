import csv,math,collections,statistics
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def read(path):
 with (P/path).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
resorts=[]
for r in read("data/national_resort_osm_reconciliation.csv"):
 if r["match_status"]!="one_unverified_facility_geometry":continue
 try:lat=float(r["latitude_candidate"]);lon=float(r["longitude_candidate"])
 except (TypeError,ValueError):continue
 resorts.append((r,lat,lon))
observations=collections.defaultdict(list)
for r in read("data/mlit_landprice_historical_panel_1983_2026.csv"):
 year=int(r["year"])
 if 1996<=year<=2026:
  try:observations[(float(r["latitude"]),float(r["longitude"]),r["land_use_raw"],r["municipality_code"])].append((year,float(r["price_yen_m2"])))
  except (ValueError,TypeError):continue
out=P/"data/ski_resort_observed_land_price_1996_2026.csv"
fields=["candidate_id","resort_name","coordinate_evidence_status","radius_km","year","point_count","median_yen_m2","matched_1996_2026_point_count","median_same_point_change_pct","sampling_warning"]
rows=[]
for resort,rlat,rlon in resorts:
 nearby={5:[],10:[],20:[]}
 for (lat,lon,landuse,municipality),series in observations.items():
  if abs(lat-rlat)>.19 or abs(lon-rlon)>.28:continue
  a=math.sin(math.radians(lat-rlat)/2)**2+math.cos(math.radians(rlat))*math.cos(math.radians(lat))*math.sin(math.radians(lon-rlon)/2)**2
  d=12742*math.asin(min(1,math.sqrt(a)))
  for radius in (5,10,20):
   if d<=radius:nearby[radius].append(series)
 for radius,series_set in nearby.items():
  byyear=collections.defaultdict(list);paired=[]
  for series in series_set:
   values=dict(series)
   for year,price in series:byyear[year].append(price)
   if 1996 in values and 2026 in values and values[1996]>0:paired.append(100*(values[2026]/values[1996]-1))
  for year in range(1996,2027):
   values=byyear[year]
   rows.append(dict(candidate_id=resort["candidate_id"],resort_name=resort["resort_name"],coordinate_evidence_status=resort["match_status"],radius_km=radius,year=year,point_count=len(values),median_yen_m2=round(statistics.median(values),2) if values else "",matched_1996_2026_point_count=len(paired),median_same_point_change_pct=round(statistics.median(paired),3) if paired else "",sampling_warning="2026-survivor sample; provisional coordinates; overlapping buffers; no climate adjustment"))
with out.open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
(P/"reports/ski_resort_30year_land_price_observed.md").write_text("# Observed 1996–2026 resort-region land prices\n\n"+f"- Provisional geocoded resort candidates: {len(resorts)}\n- Land-price point keys: {len(observations)}\n- Resort-radius-year rows: {len(rows)}\n- Radii: 5, 10, 20 km.\n- **Limitations:** 2026-survivor bias, provisional locations, overlapping buffers, no land-use or climate adjustment. Not a causal warming estimate.\n",encoding="utf-8")
assert rows and any(r["point_count"]>0 for r in rows)
print(f"Produced {len(rows)} rows for {len(resorts)} candidates")
