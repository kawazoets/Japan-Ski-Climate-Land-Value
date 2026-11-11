"""Collect official JMA historical daily snow depth, verified Furano pilot.

The JMA station 12940 (富良野) is station block 0021, region 12 on the
official past-observations site. The scraper requires the Japanese station
name and snow-depth column; a changed layout fails closed, never invents data.
Limit requests and pause between months per JMA access guidance.
"""
import csv,datetime,re,time,urllib.request
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
BASE="https://www.data.jma.go.jp/stats/etrn/view/daily_a1.php"
def month_data(year,month):
 url=f"{BASE}?prec_no=12&block_no=0021&year={year}&month={month}&day=&view=p2"
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (academic historical research; low rate)"})
 with urllib.request.urlopen(req,timeout=45) as f:html=f.read()
 soup=BeautifulSoup(html,"html.parser")
 title=soup.get_text(" ",strip=True)
 if "富良野" not in title or "最深積雪" not in title:raise ValueError("Unexpected JMA station or element in "+url)
 table=soup.select_one("#tablefix1")
 if table is None:raise ValueError("JMA observation table missing "+url)
 header=table.get_text(" ",strip=True)
 if "最深積雪" not in header:raise ValueError("Snow depth column absent "+url)
 result=[]
 for tr in table.select("tr"):
  tds=tr.find_all("td",recursive=False)
  if len(tds)<5:continue
  day=tds[0].get_text(" ",strip=True)
  if not day.isdigit() or not 1<=int(day)<=31:continue
  date=datetime.date(year,month,int(day))
  # JMA p2 main-elements table has final column = daily max snow depth.
  last=tds[-1].get_text(" ",strip=True)
  if last in ("","///","×","--","-"):depth=""
  else:
   m=re.fullmatch(r"(\d+(?:\.\d+)?)(?:\s*[)\]＃#])?",last)
   if not m:raise ValueError("Unrecognized JMA snow depth "+repr(last)+" on "+str(date))
   depth=float(m.group(1))
  result.append([ "12940",date.isoformat(),depth,"JMA official daily_a1 view=p2",url])
 if len(result)<28:raise ValueError("Too few days for "+url+" : "+str(len(result)))
 return result
def main():
 out=[]
 # Collect ten complete winter seasons, November to April, 2016–2025.
 for winter in range(2016,2026):
  for year,month in [(winter,11),(winter,12)]+[(winter+1,m) for m in (1,2,3,4)]:
   out.extend(month_data(year,month))
   time.sleep(2)
 target=ROOT/"data/jma_daily_snow_depth_2016_2026.csv"
 with target.open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["station_id","date","snow_depth_cm","source","source_url"]);w.writerows(out)
 if len(out)<1800:raise SystemExit("Incomplete historical JMA snow-depth panel")
 print("Verified actual JMA daily snow observations",len(out),"first",out[:3],"last",out[-3:])
if __name__=="__main__":main()
