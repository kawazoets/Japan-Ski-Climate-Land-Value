"""Seed nationwide coordinates from already captured OSM ski-resort geometries.

Uses local CSV only, no API requests. Never drops national candidates.
Exact-name matches are provisional, not verified geocodes.
"""
import csv,re,unicodedata,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data/national_ski_resort_candidate_master.csv"
NEAR=ROOT/"data/resort_landprice_nearest_2026.csv"
OUT=ROOT/"data/national_ski_resort_geocoded_seed.csv"
REPORT=ROOT/"reports/national_geocoding_seed_audit.md"
def normalize(s):
    s=unicodedata.normalize("NFKC",s or "").casefold()
    return re.sub(r"[\s・･\-‐–—()（）「」『』]","",s)
def read(p):
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def main():
    master=read(MASTER);near=read(NEAR)
    osm=collections.defaultdict(dict)
    for r in near:
        name=r["resort_name"]
        key=normalize(name)
        unique=(r["resort_latitude"],r["resort_longitude"],r["osm_url"])
        osm[key][unique]=r
    matches=0;ambiguous=0;pilot=0
    output=[]
    for r in master:
        options=list(osm.get(normalize(r["resort_name"]),{}).values())
        if len(options)==1:
            m=options[0];matches+=1
            lat=m["resort_latitude"];lon=m["resort_longitude"]
            url=m["osm_url"];status="provisional_exact_name_osm"
        else:
            lat=lon=url=""
            status="ambiguous_osm_geometry" if len(options)>1 else "no_osm_geometry_yet"
            ambiguous+=len(options)>1
        pilot+=r["pilot_13_flag"]=="yes"
        output.append({**r,"latitude_seed":lat,"longitude_seed":lon,"coordinate_source_url":url,"coordinate_evidence_status":status,"geocode_review":"pending","operating_status_verified":"unknown","closure_status_verified":"unknown"})
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(output[0]));w.writeheader();w.writerows(output)
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(f"""# Nationwide coordinate seeding audit

- Nationwide candidate records preserved: **{len(master)}**
- Exact-name OSM coordinate seeds from existing land-price join: **{matches}**
- Ambiguous OSM geometry matches: **{ambiguous}**
- Remaining without coordinate seeds: **{len(master)-matches}**
- Original 13-resort pilot flags preserved: **{pilot}**
- Distinct OSM resort-name keys in prior land-price join: **{len(osm)}**

These coordinates are **provisional**, not verified resort locations. The original land-price join included a limited OSM subset, so this is only a recovery of existing geocodes; it does not complete national geocoding. All directory candidates remain included.

**Critical normalization correction:** Japanese long vowel mark ー is retained. Removing it corrupts names such as スキー and リゾート, and can create false matches. No remote OSM/Nominatim calls were made.

Next: obtain a broader Japan OSM extract or carefully bounded Overpass harvest, then link with explicit geographic and name-quality checks. Public Nominatim is not used for mass geocoding.
""",encoding="utf-8")
    print(f"National records={len(master)}, coordinate seeds={matches}, missing={len(master)-matches}")
if __name__=="__main__":main()
