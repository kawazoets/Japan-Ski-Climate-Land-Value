"""Build a nationwide evidence-based resort coverage table without dropping missing cases.

Use 458 directory candidates as the fixed cohort. The 228 one-geometry
matches are provisional, not verified facility centroids.
"""
import csv,math,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def main():
    rows=read(ROOT/"data/national_resort_osm_reconciliation.csv")
    out=[]
    for r in rows:
        has_geo=r["match_status"]=="one_unverified_facility_geometry"
        out.append({"candidate_id":r["candidate_id"],"resort_name":r["resort_name"],"prefecture":r["prefecture"],"latitude":r["latitude_candidate"] if has_geo else "","longitude":r["longitude_candidate"] if has_geo else "","coordinate_source":r["osm_source_url"] if has_geo else "","coordinate_quality":"unverified_osm_single_geometry" if has_geo else r["match_status"],"historical_operating_days_2016_2026":"not_collected","snow_depth_daily_2016_2026":"not_collected","historical_land_price_2016_2026":"not_collected","municipality_boundary_join":"not_performed","resort_operating_status":"not_verified","closed_resort_inclusion":"retained","analysis_eligible":"no","blocking_reason":"operating_days_and_historical_prices_missing"})
    path=ROOT/"data/national_climate_landvalue_evidence_matrix.csv"
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    n=sum(bool(x["latitude"]) for x in out)
    report=ROOT/"reports/national_climate_landvalue_evidence_status.md"
    report.write_text(f"""# Nationwide climate × land-value evidence matrix

- Nationwide candidate records: **{len(out)}**
- Provisional OSM coordinate candidates: **{n}**
- Records without unique facility geometry: **{len(out)-n}**
- Resort operating-day time series collected: **0**
- 2016–2026 daily snow-depth time series collected: **0**
- Historical 2016–2026 land-price series linked: **0**
- Records eligible for causal/statistical analysis: **0**

The cohort is the directory candidate list, not a verified census of currently operating ski areas. It retains closed/paused facilities to prevent survival bias. A matched OSM polygon or way is not a validated resort centroid. Weather-station data cannot substitute for actual operating days. **No climate–land-price association has yet been estimated.**

Next independent work packages: official 2016–2026 land-price point acquisition, municipality and resort coordinate validation, operating-day historical sourcing, and JMA snow series acquisition with quality codes.
""",encoding="utf-8")
    print(f"records={len(out)} provisional_coordinates={n} analysis_eligible=0")
    if len(out)<400:raise SystemExit("National cohort changed unexpectedly")
if __name__=="__main__":main()
