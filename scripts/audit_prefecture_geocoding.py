"""Audit the research sampling frame and prioritize missing geographic coverage."""
import csv,collections,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def pref(s):
    m=re.match(r"^(北海道|東京都|京都府|大阪府|.{2,3}県)",s or "")
    return m.group(1) if m else ""
def main():
    candidates=read(ROOT/"data/national_resort_osm_reconciliation.csv")
    statuses={}
    for line in (ROOT/"reports/osm_national_geocoding_harvest.md").read_text(encoding="utf-8").splitlines():
        m=re.match(r"^- (.+?) \| (ok|failed) \| (\d+) \|",line)
        if m:statuses[m.group(1)]=m.group(2)
    counts=collections.defaultdict(collections.Counter)
    for r in candidates:
        p=r["prefecture"];counts[p]["directory"]+=1
        counts[p][r["match_status"]]+=1
    fields=["prefecture","harvest_status","directory_candidates","single_geometry_candidates","ambiguous_facility_candidates","piste_only_candidates","no_exact_match","coverage_fraction","priority"]
    rows=[]
    for p in sorted(statuses):
        c=counts[p];n=c["directory"];single=c["one_unverified_facility_geometry"]
        status=statuses[p]
        priority="retry_osm" if status!="ok" and n>0 else ("review_names_and_facility_geometries" if n>single else "monitor")
        rows.append(dict(prefecture=p,harvest_status=status,directory_candidates=n,single_geometry_candidates=single,ambiguous_facility_candidates=c["multiple_facility_geometries_manual_review"],piste_only_candidates=c["piste_only_or_nonfacility_match"],no_exact_match=c["no_exact_name_match"],coverage_fraction=f"{single/n:.3f}" if n else "",priority=priority))
    out=ROOT/"data/prefecture_resort_geocoding_coverage.csv"
    with out.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    failed=[r for r in rows if r["harvest_status"]!="ok"]
    report="# National ski resort geocoding coverage\n\n"
    report+=f"- Directory candidate records: **{len(candidates)}**\n- Single unverified facility geometry candidates: **{sum(int(r['single_geometry_candidates']) for r in rows)}**\n- Failed prefectures: **{len(failed)}**\n- Directory candidates in failed prefectures: **{sum(int(r['directory_candidates']) for r in failed)}**\n\n"
    report+="## Failed-prefecture priority (by directory count)\n\n"
    for r in sorted(failed,key=lambda x:-int(x["directory_candidates"])):
        report+=f"- {r['prefecture']}: {r['directory_candidates']} directory candidates; {r['single_geometry_candidates']} single-geometry matches\n"
    report+="\n## Methodological limits\n\nThis is an evidence-coverage audit, not a resort closure or ski-season analysis. Exact-name OSM geometry matches are unverified, and missing matches must not be treated as missing resorts. Counts of facilities and counts of OSM piste geometries are different. Climate/land-price inference is not supported until resort operating-day records and appropriate geographic controls are joined.\n"
    (ROOT/"reports/prefecture_geocoding_coverage.md").write_text(report,encoding="utf-8")
    print(report)
    if len(candidates)<300 or len(statuses)!=47:raise SystemExit("Incomplete national input")
if __name__=="__main__":main()
