"""Conservative, offline reconciliation. Never conflate piste names with ski resorts."""
import csv,re,unicodedata,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def norm(s):
    s=unicodedata.normalize("NFKC",s or "").casefold()
    return re.sub(r"[\s・･　\-‐–—()（）「」『』]","",s)
def prefecture(s):
    m=re.match(r"^(北海道|東京都|京都府|大阪府|.{2,3}県)",s or "")
    return m.group(1) if m else ""
def directory_prefecture(d):
    region=d.get("region_raw","")
    heading=d.get("prefecture_heading_raw","")
    name=d.get("resort_name","")
    # The source switches between prefecture headings and single-prefecture
    # regional headings (e.g. 長野64 か所), and then a separate closure list.
    if "営業休止・閉鎖" in region:
        prefectures="北海道 青森県 岩手県 宮城県 秋田県 山形県 福島県 茨城県 栃木県 群馬県 埼玉県 千葉県 東京都 神奈川県 新潟県 富山県 石川県 福井県 山梨県 長野県 岐阜県 静岡県 愛知県 三重県 滋賀県 京都府 大阪府 兵庫県 奈良県 和歌山県 鳥取県 島根県 岡山県 広島県 山口県 徳島県 香川県 愛媛県 高知県 福岡県 佐賀県 長崎県 熊本県 大分県 宮崎県 鹿児島県 沖縄県".split()
        pattern="("+"|".join(prefectures)+")"
        m=re.search(pattern+r"[・･](?:閉鎖|休業|営業休止|今季休業)$",name)
        if not m:
            m=re.search(pattern+r"(?:閉鎖|休業|営業休止|今季休業)$",name)
        return m.group(1) if m else ""
    if region.startswith("北海道"):return "北海道"
    # Regional heading is authoritative for dedicated prefecture sections.
    for label,p in (("長野","長野県"),("新潟","新潟県")):
        if re.match(r"^"+label+r"\d",region):return p
    return prefecture(heading) or prefecture(region)

def main():
    directory=read(ROOT/"data/national_ski_resort_candidate_master.csv")
    osm=read(ROOT/"data/osm_national_ski_area_geometries.csv")
    idx=collections.defaultdict(list)
    for r in osm:
        if r.get("latitude") and r.get("longitude") and r.get("name"):
            idx[(prefecture(r.get("prefecture_query","")),norm(r["name"]))].append(r)
    rows=[];counts=collections.Counter()
    for d in directory:
        pref=directory_prefecture(d)
        candidates=idx.get((pref,norm(d["resort_name"])),[])
        # Piste-only matches are never accepted as facility coordinates.
        facility=[r for r in candidates if r.get("landuse")=="winter_sports" or r.get("sport")=="skiing" and not r.get("piste_type")]
        if len(facility)==1:
            status="one_unverified_facility_geometry";best=facility[0]
        elif len(facility)>1:
            status="multiple_facility_geometries_manual_review";best={}
        elif candidates:
            status="piste_only_or_nonfacility_match";best={}
        else:
            status="no_exact_name_match";best={}
        row={"candidate_id":d["candidate_id"],"resort_name":d["resort_name"],"prefecture":pref,"matching_osm_geometries":len(candidates),"matching_facility_geometries":len(facility),"latitude_candidate":best.get("latitude",""),"longitude_candidate":best.get("longitude",""),"osm_source_url":best.get("source_url",""),"match_status":status,"operating_status":"not_verified","research_inclusion":"retain_candidate"}
        rows.append(row);counts[status]+=1
    if sum(not x["prefecture"] for x in rows):
        raise SystemExit("Some candidate prefectures remain unresolved; refusing to publish misleading coverage")
    out=ROOT/"data/national_resort_osm_reconciliation.csv"
    with out.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    audit=(ROOT/"reports/osm_national_geocoding_harvest.md").read_text(encoding="utf-8")
    coverage=re.search(r"Successful prefectures:\s*(\d+)",audit)
    successful=int(coverage.group(1)) if coverage else -1
    report="# Nationwide resort–OSM reconciliation\n\n"
    report+=f"- Directory candidate records retained: **{len(rows)}**\n- OSM named geometries: **{len(osm)}**\n- Prefectures successfully harvested: **{successful}/47**\n"
    report+="\n## Exact-name match classification\n\n"
    report+="".join(f"- {k}: **{v}**\n" for k,v in sorted(counts.items()))
    report+="\nCoordinates are unverified OSM candidates, not verified resort entrances. Individual piste features are excluded from accepted coordinates. All directory candidates are retained. Missing matches can reflect missing OSM coverage, failed prefecture queries, name variations or genuinely absent features; they are not evidence of resort closure. No resort operating-day data has been established.\n"
    (ROOT/"reports/national_resort_osm_reconciliation.md").write_text(report,encoding="utf-8")
    print(report)
    if len(rows)<300:raise SystemExit("Nationwide inventory unexpectedly small")
if __name__=="__main__":main()
