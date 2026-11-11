"""Merge matrix outputs and report complete/failed prefecture coverage."""
import csv,glob
from pathlib import Path
from collect_one_prefecture_osm import FIELDS,PREFS
records={};statuses=[]
for p in glob.glob("parts/**/status_*.txt",recursive=True):statuses.extend(Path(p).read_text(encoding="utf-8").splitlines())
for p in glob.glob("parts/**/pref_*.csv",recursive=True):
    with open(p,encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):records[(r["osm_type"],r["osm_id"])]=r
out=Path("data/osm_national_ski_area_geometries.csv");out.parent.mkdir(exist_ok=True)
with out.open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(sorted(records.values(),key=lambda r:(r["prefecture_query"],r["name"],r["osm_id"])))
report=Path("reports/osm_national_geocoding_harvest.md");report.parent.mkdir(exist_ok=True)
success=sum("\tok\t" in x for x in statuses)
report.write_text(f"# Nationwide OSM harvest\n\n- Prefectures expected: {len(PREFS)}\n- Prefectures with status files: {len(statuses)}\n- Successful prefectures: {success}\n- Distinct named geometries: {len(records)}\n- Failed or missing prefectures: {len(PREFS)-success}\n\n## Per-prefecture results\n\n"+ "\n".join("- "+x.replace("\t"," | ") for x in sorted(statuses))+"\n\nThese OSM geometries include ski pistes, not necessarily distinct resorts. National directory candidates are preserved separately.\n",encoding="utf-8")
print(f"success={success}/{len(PREFS)}, geometries={len(records)}")
if success==0:raise SystemExit("All prefecture requests failed")
