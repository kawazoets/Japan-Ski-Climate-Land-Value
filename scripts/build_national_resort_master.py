"""Preserve nationwide ski-area candidate universe; annotate evidence, never silently drop rows.

Directory is a candidate source, not the official 417 operational count.
OSM coordinates are optional, and matched only on conservative normalized names.
"""
import csv,re,unicodedata,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):
    if not path.exists():return []
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def norm(s):
    s=unicodedata.normalize("NFKC",s or "").casefold()
    s=re.sub(r"[\s・･　\-‐–—ー()（）「」『』]","",s)
    return s
def main():
    directory=read(ROOT/"data/directory_candidates.csv")
    if len(directory)<300:raise SystemExit(f"Expected nationwide directory, got {len(directory)} rows")
    osm=read(ROOT/"data/osm_ski_candidates.csv")
    geo=read(ROOT/"data/jma_nearest_snow_stations.csv")
    osm_index=collections.defaultdict(list)
    for r in osm:
        key=norm(r.get("name"))
        if key and r.get("latitude") and r.get("longitude"):osm_index[key].append(r)
    pilot={norm(r["resort_name"]) for r in geo if r.get("station_rank")=="1"}
    seen=collections.Counter()
    rows=[]
    for i,r in enumerate(directory,1):
        name=r.get("resort_name","").strip();key=norm(name);seen[key]+=1
        candidates=osm_index.get(key,[])
        # Multiple exact name matches are ambiguous even if coordinates are close.
        match=candidates[0] if len(candidates)==1 else {}
        rows.append({"candidate_id":f"DIR-{i:04d}","resort_name":name,"region_raw":r.get("region",""),"prefecture_heading_raw":r.get("prefecture_heading",""),"source_url":r.get("source_url",""),"candidate_status":"unverified_directory_candidate","duplicate_name_group":key,"duplicate_name_occurrences":0,"osm_exact_name_match_count":len(candidates),"latitude_candidate":match.get("latitude",""),"longitude_candidate":match.get("longitude",""),"osm_source_url":match.get("source_url",""),"coordinate_status":"unverified_exact_name_candidate" if match else ("ambiguous_name" if len(candidates)>1 else "not_matched"),"operating_status":"not_verified","closure_status":"not_verified","pilot_13_flag":"yes" if key in pilot else "no","jma_station_status":"not_checked","municipality_code_status":"not_verified","research_inclusion":"retain_candidate"})
    for r in rows:r["duplicate_name_occurrences"]=seen[r["duplicate_name_group"]]
    out=ROOT/"data/national_ski_resort_candidate_master.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    matched=sum(r["coordinate_status"]=="unverified_exact_name_candidate" for r in rows)
    duplicate=sum(r["duplicate_name_occurrences"]>1 for r in rows)
    report=ROOT/"reports/national_resort_coverage_audit.md"
    report.parent.mkdir(exist_ok=True)
    report.write_text(f"""# Nationwide candidate coverage audit

- Directory candidate records retained: **{len(rows)}**
- Records in duplicate normalized-name groups: **{duplicate}**
- Unique-name candidates with an exact-name OSM coordinate candidate: **{matched}**
- OSM raw candidate records available: **{len(osm)}**
- Prior pilot resort names found in nationwide directory: **{sum(r['pilot_13_flag']=='yes' for r in rows)}**
- Remaining candidate records without unambiguous exact-name coordinates: **{len(rows)-matched}**

**No candidates were discarded for missing coordinates, land-price points, station matches, or unknown closure status.**

The directory is an unverified third-party list and is not the Japan Ropeway Association's count of 417 operating ski areas. Counts are not interchangeable. Exact-name matches are **candidate coordinates, not verified facility locations**; duplicated names are withheld from automatic geocoding. The 13-resort pilot is a subset, not the national sampling frame.

## Next stages
1. Obtain/validate nationwide geocodes with source attribution and confidence; avoid conflating lift stations and resort polygons.
2. Verify operating/closed status, including historically closed areas, with date-specific evidence.
3. Assign municipality by administrative boundary polygons (not nearest land-price point).
4. Connect JMA station records and resort operating seasons, preserving coverage and missingness.
5. Compare matched-point land-price trends with controls and sensitivity checks.

Sources: `data/directory_candidates.csv` and optional `data/osm_ski_candidates.csv`.
""",encoding="utf-8")
    print(f"Nationwide candidates={len(rows)}, OSM exact-name candidates={matched}, pilot matches={sum(r['pilot_13_flag']=='yes' for r in rows)}")
if __name__=="__main__":main()
