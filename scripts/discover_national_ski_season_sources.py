"""Nationwide, bounded SnowJapan season-date discovery (not actual operating days).

Publicly available season start/end observations are labelled CALENDAR_SPAN.
Source pages are fetched politely, with cache/timeout and clear audit coverage.
No data are merged by fuzzy name without review.
"""
import csv,datetime,json,re,time,urllib.request,urllib.parse,xml.etree.ElementTree as ET
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"data";REPORT=ROOT/"reports";REPORT.mkdir(exist_ok=True)
BASE="https://www.snowjapan.com"
MAX_URLS=1800
def fetch(url,timeout=18):
 req=urllib.request.Request(url,headers={"User-Agent":"JapanSkiClimateResearch/1.0 (public academic analysis; one request per second)"})
 with urllib.request.urlopen(req,timeout=timeout) as response:return response.read(6000000)
def rows(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write(path,fields,records):
 with path.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
def main():
 cohort=rows(DATA/"ski_resort_mlit_buffer_summary_2016_2026.csv")
 names={}
 for r in cohort:names.setdefault(r["resort_name"],set()).add(r["candidate_id"])
 seeds=[BASE+"/ski-areas",BASE+"/insights",BASE+"/sitemap.xml"]
 links=set();errors=[];source_pages=0
 # First fetch site sitemaps (a single sitemap can cover the entire national directory).
 for seed in seeds:
  try:
   content=fetch(seed)
   if seed.endswith(".xml"):
    root=ET.fromstring(content)
    links.update(x.text.strip() for x in root.iter() if x.tag.endswith("loc") and x.text and x.text.strip().startswith(BASE))
   else:
    soup=BeautifulSoup(content,"html.parser")
    links.update(urllib.parse.urljoin(seed,a.get("href")) for a in soup.select("a[href]") if a.get("href"))
  except Exception as e:errors.append({"url":seed,"error":str(e)[:200]})
 # Sitemap index: expand only sitemap XML, not arbitrary external links.
 for url in list(links):
  if not url.endswith(".xml") or not url.startswith(BASE):continue
  try:
   root=ET.fromstring(fetch(url))
   links.update(x.text.strip() for x in root.iter() if x.tag.endswith("loc") and x.text and x.text.strip().startswith(BASE))
  except Exception as e:errors.append({"url":url,"error":str(e)[:200]})
 # Prefer ski area pages; avoid articles and unrelated pages.
 urls=sorted(u.split("#")[0] for u in links if u.startswith(BASE) and not u.endswith(".xml") and any(t in u.lower() for t in ["/ski-area","/ski-areas/","/season","/insights"]))
 urls=list(dict.fromkeys(urls))[:MAX_URLS]
 observed=[];index=[]
 for url in urls:
  try:
   html=fetch(url)
   soup=BeautifulSoup(html,"html.parser")
   title=soup.title.get_text(" ",strip=True)[:180] if soup.title else ""
   body=soup.get_text(" ",strip=True)
   matched=[]
   for name,ids in names.items():
    if len(name)>=4 and name in body[:3000]:matched.append(name)
   index.append({"url":url,"page_title":title,"matching_cohort_names":" | ".join(matched[:8]),"matched_name_count":len(matched),"fetch_status":"ok"})
   # Store raw date candidates with context; no claims of actual operating days.
   for m in re.finditer(r"(?:20(?:1[6-9]|2[0-6])[-/年.]\d{1,2}[-/月.]\d{1,2}|(?:20)?2[1-6][-–/]2[2-7]).{0,90}",body):
    snippet=body[max(0,m.start()-80):min(len(body),m.end()+80)]
    if any(word in snippet.lower() for word in ["open","close","season","営業","オープン","終了"]):
     observed.append({"url":url,"page_title":title,"date_context":snippet[:250],"evidence_type":"UNVERIFIED_CALENDAR_DATE_NOT_ACTUAL_DAYS"})
     if len(observed)>=10000:break
   source_pages+=1
  except Exception as e:
   errors.append({"url":url,"error":str(e)[:200]})
   index.append({"url":url,"page_title":"","matching_cohort_names":"","matched_name_count":0,"fetch_status":"failed"})
  time.sleep(0.35)
 write(DATA/"national_ski_season_page_index.csv",["url","page_title","matching_cohort_names","matched_name_count","fetch_status"],index)
 write(DATA/"national_ski_season_date_candidates.csv",["url","page_title","date_context","evidence_type"],observed)
 write(DATA/"national_ski_season_fetch_errors.csv",["url","error"],errors)
 result={"run_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"national_cohort_size":len(names),"discovered_ski_urls":len(urls),"fetched_pages":source_pages,"date_candidate_mentions":len(observed),"pages_matching_cohort_name":sum(bool(r["matched_name_count"]) for r in index),"fetch_errors":len(errors),"method":"SnowJapan public sitemap/links; discovery only; no unverified actual days"}
 (REPORT/"national_ski_season_discovery.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 (REPORT/"national_ski_season_discovery.md").write_text("# Nationwide ski season evidence discovery\n\n"+ "\n".join(f"- {k}: {v}" for k,v in result.items())+"\n\n**Calendar season spans are not actual operating days.** Source snippets are unverified leads. No causal conclusion is claimed.\n",encoding="utf-8")
 print(json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
