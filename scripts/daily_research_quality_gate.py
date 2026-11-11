"""Daily offline research quality gate; fail closed on incomplete or inconsistent data."""
import csv,json,datetime,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/name).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def main():
    master=read("data/national_ski_resort_candidate_master.csv")
    geo=read("data/national_resort_osm_reconciliation.csv")
    matrix=read("data/national_climate_landvalue_evidence_matrix.csv")
    season=read("data/resort_operating_season_evidence.csv")
    ids=[r["candidate_id"] for r in master]
    if len(ids)<400 or len(ids)!=len(set(ids)):raise SystemExit("Missing/duplicate candidate IDs")
    for label,rs in (("geocoding",geo),("matrix",matrix)):
        if [r["candidate_id"] for r in rs]!=ids:raise SystemExit(label+" cohort IDs or order disagree with master")
    if any(not r["prefecture"] for r in geo):raise SystemExit("Unresolved prefecture")
    if any("エリア別スキー場ガイド" in r["resort_name"] for r in master):raise SystemExit("Editorial navigation links reintroduced")
    if any(r["match_status"]!="one_unverified_facility_geometry" and (r["latitude_candidate"] or r["longitude_candidate"]) for r in geo):raise SystemExit("Ambiguous coordinates accepted")
    with_geo=sum(r["match_status"]=="one_unverified_facility_geometry" for r in geo)
    if with_geo!=sum(bool(r["latitude"]) and bool(r["longitude"]) for r in matrix):raise SystemExit("Coordinate coverage disagrees")
    closed=sum("営業休止・閉鎖" in r["region_raw"] for r in master)
    with_days=sum(bool(r.get("observed_operating_days")) for r in season)
    now=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    report=f"""# Automated national research quality gate

Last successful check: **{now}**

- Directory facility candidates: **{len(master)}** (not official operating-resort census)
- Provisional single-geometry OSM matches: **{with_geo}**
- Missing/ambiguous coordinates: **{len(master)-with_geo}**
- Entries in directory closure/paused section: **{closed}** (source labels, unverified)
- Source-backed resort-season observations: **{len(season)}**
- Resort-season rows with actual operating days: **{with_days}**
- Historical land-price input records: **{len(read("data/land_prices.csv"))}**
- Quality-gate result: **PASS**

The quality gate validates structural consistency, not truth of unverified third-party source data. Zero observations are reported as zero, not inferred. No climate–land-price estimate is supported without longitudinal outcome and exposure data.
"""
    (ROOT/"reports/automated_research_quality_gate.md").write_text(report,encoding="utf-8")
    print(report)
if __name__=="__main__":main()
