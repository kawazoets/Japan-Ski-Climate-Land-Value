"""Discover JMA historical station block numbers from official station selectors.

Never assume the five-digit AMeDAS station ID is the JMA historical block_no.
Resolve by station name and prefecture, and retain ambiguities for review.
"""
import csv,re,time,urllib.request,urllib.parse,collections
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
BASE="https://www.data.jma.go.jp/stats/etrn/select/prefecture00.php"
def main():
 with (ROOT/"data/national_jma_snow_station_candidates.csv").open(encoding="utf-8-sig",newline="") as f:candidates=list(csv.DictReader(f))
 wanted={r["jma_station_name"] for r in candidates}
 discovered=collections.defaultdict(set);errors=[]
 for prec in range(1,100):
  url=f"{BASE}?prec_no={prec:02d}"
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (noncommercial climate research)"})
   with urllib.request.urlopen(req,timeout=20) as response:html=response.read()
   soup=BeautifulSoup(html,"html.parser")
   for a in soup.find_all("a",href=True):
    href=urllib.parse.urljoin(url,a["href"])
    q=urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
    block=q.get("block_no",[""])[0]
    name=a.get_text(" ",strip=True)
    if block and name in wanted:
     discovered[name].add((prec,block))
  except Exception as e:errors.append(f"{prec:02d}: {type(e).__name__}: {str(e)[:100]}")
  time.sleep(0.15)
 rows=[]
 for name in sorted(wanted):
  matches=sorted(discovered.get(name,set()))
  if len(matches)==1:
   prec,block=matches[0];status="unique_name_match"
  else:prec=block="";status="unresolved" if not matches else "ambiguous_name_match"
  rows.append([name,prec,block,status,len(matches),";".join(f"{a:02d}:{b}" for a,b in matches)])
 out=ROOT/"data/jma_historical_block_number_candidates.csv"
 with out.open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["jma_station_name","prec_no","block_no","resolution_status","candidate_count","candidate_prec_block_pairs"]);w.writerows(rows)
 report=ROOT/"reports/jma_historical_station_resolution.md"
 report.write_text(f"# JMA historical station selector discovery\n\nOfficial selector: {BASE}\n\n- Distinct station names requested: {len(wanted)}\n- Unique name matches: {sum(x[3]=='unique_name_match' for x in rows)}\n- Ambiguous names: {sum(x[3]=='ambiguous_name_match' for x in rows)}\n- Unresolved names: {sum(x[3]=='unresolved' for x in rows)}\n- Prefecture selector HTTP errors: {len(errors)}\n\nStation names can collide; unique names are provisional until coordinates are verified. No daily observations are inferred.\n\n## Selector errors (first 15)\n"+"\n".join("- "+e for e in errors[:15])+"\n",encoding="utf-8")
 print(report.read_text())
if __name__=="__main__":main()
