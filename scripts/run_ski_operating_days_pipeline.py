"""Scheduled evidence audit; source snippets are NEVER verified operating days."""
import csv,datetime,json,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"data";R=ROOT/"reports";R.mkdir(exist_ok=True)
SOURCES=[("memuro","https://www.memuro.net/administration/soshiki/keiei/kanrisya/files/R2jhkokuminn.pdf"),("nagano_policy","https://www.pref.nagano.lg.jp/kankoshin/documents/20_sukizyouhoushin_hontai.pdf"),("nagano_survey","https://www.pref.nagano.lg.jp/kankoshin/documents/30_zittaityousakekka.pdf"),("bibai_plan","https://www.city.bibai.hokkaido.jp/uploaded/attachment/16752.pdf"),("mutsu_kamafuse","https://www.city.mutsu.lg.jp/government/gyosei/shiteikanri/files/03_R5_undou_ski.pdf"),("itoigawa_2023","https://www.city.itoigawa.lg.jp/uploaded/attachment/8253.pdf")]
def read(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def save(path,cols,rows):
 with path.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
def main():
 import fitz
 leads=[];fetches=[]
 for key,url in SOURCES:
  record={"source_id":key,"url":url,"status":"failed","error":""}
  try:
   request=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
   with urllib.request.urlopen(request,timeout=35) as response:blob=response.read(18000000)
   if not blob.startswith(b"%PDF"):raise ValueError("Not a PDF")
   pdf=fitz.open(stream=blob,filetype="pdf")
   for page_no,page in enumerate(pdf):
    body=page.get_text()
    for match in re.finditer(r"(?:営業日数|営業日|稼働日数|稼働日).{0,55}",body):
     excerpt=" ".join(body[max(0,match.start()-50):match.end()+60].split())
     leads.append({"source_id":key,"source_url":url,"page":page_no+1,"snippet":excerpt[:250],"status":"UNVERIFIED"})
     if sum(r["source_id"]==key for r in leads)>=75:break
    if sum(r["source_id"]==key for r in leads)>=75:break
   record["status"]="parsed"
  except Exception as exc:record["error"]=str(exc)[:240]
  fetches.append(record)
 save(D/"ski_operating_day_source_leads.csv",["source_id","source_url","page","snippet","status"],leads)
 save(D/"ski_operating_day_source_fetch.csv",["source_id","url","status","error"],fetches)
 land=read(D/"ski_resort_mlit_buffer_summary_2016_2026.csv")
 names={}
 for row in land:names.setdefault(row["resort_name"],set()).add(row["candidate_id"])
 verified=read(D/"municipal_ski_actual_operating_days_verified.csv")
 existing=read(D/"resort_operating_season_evidence.csv")
 matched=[];unmatched=[]
 for r in verified:
  if r["evidence_status"]!="verified" or not r["observed_operating_days"].isdigit():continue
  ids=names.get(r["resort_name"],set())
  if len(ids)==1:
   matched.append({"candidate_id":next(iter(ids)),"season_start_year":r["season_start_year"],"actual_operating_days":r["observed_operating_days"],"source_url":r["source_url"]})
  else:unmatched.append(r["resort_name"])
 for r in existing:
  if r["evidence_status"]=="verified" and r["candidate_id"] and r["observed_operating_days"].isdigit():
   matched.append({"candidate_id":r["candidate_id"],"season_start_year":r["season_start_year"],"actual_operating_days":r["observed_operating_days"],"source_url":r["source_url"]})
 save(D/"ski_actual_operating_days_joined.csv",["candidate_id","season_start_year","actual_operating_days","source_url"],matched)
 seasons={}
 for row in matched:seasons.setdefault(row["candidate_id"],set()).add(row["season_start_year"])
 eligible=sum(len(v)>=2 for v in seasons.values())
 state="READY_FOR_LIMITED_ANALYSIS" if eligible>=5 else "BLOCKED_INSUFFICIENT_OPERATING_DAY_EVIDENCE"
 status={"date_utc":datetime.datetime.now(datetime.timezone.utc).date().isoformat(),"status":state,"matched_actual_operating_day_rows":len(matched),"resorts_with_two_or_more_seasons":eligible,"unverified_official_pdf_leads":len(leads),"unmatched_verified_resorts":sorted(set(unmatched)),"source_fetches":fetches,"requires_user_action":False}
 (R/"ski_autonomous_pipeline_status.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 (R/"ski_autonomous_pipeline_status.md").write_text("# Automated ski operating-day evidence audit\n\n"+f"Status: **{state}**\n\nVerified cohort-matched operating-day rows: {len(matched)}\n\nResorts with at least two seasons: {eligible}\n\nUnverified source snippets: {len(leads)}\n\nUnmatched municipal resort names: {', '.join(sorted(set(unmatched))) or 'none'}\n\nSource candidates are **not** verified operating days. No causal result can be produced until actual operating-day evidence is sufficient. Planned opening dates and calendar spans must never be substituted.\n",encoding="utf-8")
 print(json.dumps(status,ensure_ascii=False))
if __name__=="__main__":main()
