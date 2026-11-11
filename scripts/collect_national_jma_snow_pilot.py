"""Download official JMA daily snow observations for nationwide station pilot.

Stage 1: 2024-25 winter, unique verified station names only, max 15 stations
selected to cover resorts with a station within 10km. Do not silently accept
non-snow pages, absent tables or unrecognized values.
"""
import csv,datetime,re,time,urllib.request,collections
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
def fetch(prec,block,name,year,month):
 page="daily_s1.php" if len(str(block))==5 else "daily_a1.php"
 url=f"https://www.data.jma.go.jp/stats/etrn/view/{page}?prec_no={prec}&block_no={block}&year={year}&month={month}&day=&view=p2"
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (academic noncommercial climate research)"})
 with urllib.request.urlopen(req,timeout=40) as response:html=response.read()
 soup=BeautifulSoup(html,"html.parser")
 title=soup.get_text(" ",strip=True)
 if name not in title or "最深積雪" not in title:raise ValueError("Station/snow column mismatch "+url)
 table=soup.select_one("#tablefix1")
 if not table or "最深積雪" not in table.get_text(" ",strip=True):raise ValueError("Snow table missing "+url)
 result=[]
 for tr in table.select("tr"):
  tds=tr.find_all("td",recursive=False)
  if len(tds)<5:continue
  day=tds[0].get_text(" ",strip=True)
  if not day.isdigit() or not 1<=int(day)<=31:continue
  date=datetime.date(year,month,int(day))
  if page=="daily_s1.php":
   if len(tds)<19:raise ValueError("Unexpected synoptic station row width "+str(len(tds)))
   val=tds[18].get_text(" ",strip=True)
  else:val=tds[-1].get_text(" ",strip=True)
  if val in ("","///","×","--","-"):depth=""
  else:
   m=re.fullmatch(r"(\d+(?:\.\d+)?)(?:\s*[)\]＃#])?",val)
   if not m:raise ValueError("Unrecognized snow cell "+repr(val)+" "+url)
   depth=float(m.group(1))
  result.append([name,date.isoformat(),depth,url])
 if len(result)<28:raise ValueError("Insufficient daily observations "+url)
 return result
def main():
 with (ROOT/"data/jma_historical_block_number_candidates.csv").open(encoding="utf-8-sig",newline="") as f:blocks={r["jma_station_name"]:r for r in csv.DictReader(f)}
 with (ROOT/"data/national_jma_snow_station_candidates.csv").open(encoding="utf-8-sig",newline="") as f:candidates=list(csv.DictReader(f))
 nearest=sorted((r for r in candidates if r["station_rank"]=="1" and float(r["straight_line_distance_km"])<=10),key=lambda r:float(r["straight_line_distance_km"]))
 selected=[];seen=set()
 for r in nearest:
  name=r["jma_station_name"];b=blocks.get(name)
  if not b or b["resolution_status"]!="unique_name_match" or name in seen:continue
  selected.append((r,b));seen.add(name)
  if len(selected)==15:break
 output=[];status=[]
 for r,b in selected:
  name=r["jma_station_name"];station=r["jma_station_id"];partial=[]
  try:
   for year,month in [(2024,11),(2024,12),(2025,1),(2025,2),(2025,3),(2025,4)]:
    month_rows=fetch(b["prec_no"],b["block_no"],name,year,month)
    partial.extend([[station]+row for row in month_rows])
    time.sleep(0.8)
   if len(partial)<180:raise ValueError("Incomplete season")
   output.extend(partial);status.append([station,name,"collected",len(partial),""])
   print("COLLECTED",station,name,len(partial),flush=True)
  except Exception as e:
   status.append([station,name,"failed",0,str(e)[:250]])
   print("FAILED",station,name,str(e),flush=True)
 out=ROOT/"data/jma_nationwide_snow_pilot_2024_winter.csv"
 with out.open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["station_id","station_name","date","snow_depth_cm","source_url"]);w.writerows(output)
 audit=ROOT/"data/jma_nationwide_snow_pilot_collection_status.csv"
 with audit.open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(["station_id","station_name","status","daily_rows","error"]);w.writerows(status)
 print("Stations selected",len(selected),"successful",sum(s[2]=="collected" for s in status),"daily rows",len(output))
if __name__=="__main__":main()
