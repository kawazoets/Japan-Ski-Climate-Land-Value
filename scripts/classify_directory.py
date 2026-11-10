"""Classify directory entries conservatively; retain source rows for audit."""
import csv,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"data"
SOURCE=ROOT/"directory_candidates.csv"
OUT=ROOT/"directory_classified.csv"
def norm(x):
    return re.sub(r"[\s・･\-‐－]+","",unicodedata.normalize("NFKC",x)).casefold()
def classify(row):
    region=row["region"].strip()
    name=row["resort_name"].strip()
    if region=="関連ページ":return "non_resort_navigation"
    if name in {"スキー場一覧","全国スキー場一覧"}:return "non_resort_heading"
    if region=="営業休止・閉鎖の情報があるスキー場":return "possibly_closed"
    if not region:return "unclassified"
    return "operating_unverified"
def main():
    with SOURCE.open(encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
    seen={}
    for row in rows:
        row["candidate_class"]=classify(row)
        row["normalized_name"]=norm(row["resort_name"])
        key=row["normalized_name"]
        if key in seen:
            row["possible_duplicate_of"]=seen[key]
        else:
            row["possible_duplicate_of"]=""
            seen[key]=row["resort_name"]
    with OUT.open("w",encoding="utf-8",newline="") as f:
        fields=list(rows[0])+["candidate_class","normalized_name","possible_duplicate_of"] if rows else []
        # Keys added to row already; avoid duplicates
        fields=list(dict.fromkeys(fields))
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    from collections import Counter
    print("Candidate classifications:",dict(Counter(r["candidate_class"] for r in rows)))
    print("Possible name duplicates:",sum(bool(r["possible_duplicate_of"]) for r in rows))
if __name__=="__main__":main()
