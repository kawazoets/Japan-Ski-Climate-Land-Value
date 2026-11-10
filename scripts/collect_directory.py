"""Retrieve a public ski-resort directory as an unverified candidate index.
Does NOT claim equivalence with the Japan Ropeway Association's 417 resorts.
"""
import csv, re, urllib.request
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime, timezone

URL="https://sunouperson.com/resorts/"
class Parser(HTMLParser):
    def __init__(self):
        super().__init__();self.in_li=0;self.in_heading=0;self.heading="";self.region="";self.prefecture="";self.items=[];self.buf=""
    def handle_starttag(self,tag,attrs):
        if tag in ("h2","h3"):self.in_heading=tag;self.heading=""
        if tag=="li":self.in_li+=1;self.buf=""
    def handle_data(self,data):
        if self.in_heading:self.heading+=data
        if self.in_li:self.buf+=data
    def handle_endtag(self,tag):
        if tag==self.in_heading:
            name=re.sub(r"\s+"," ",self.heading).strip()
            if tag=="h2":self.region=name
            if tag=="h3":self.prefecture=name
            self.in_heading=0
        if tag=="li" and self.in_li:
            name=re.sub(r"\s+"," ",self.buf).strip()
            name=re.sub(r"詳しい情報$","",name).strip()
            if name and name not in ("スキー場一覧", "全国スキー場一覧") and ("スキー" in name or "スノー" in name or "リゾート" in name or "高原" in name or "ゲレンデ" in name or "白馬" in name or "安比" in name or "GALA" in name):
                self.items.append((self.region,self.prefecture,name))
            self.in_li-=1
def main():
    req=urllib.request.Request(URL,headers={"User-Agent":"JapanSkiClimateLandValue/0.1 research directory reader"})
    with urllib.request.urlopen(req,timeout=45) as r: html=r.read().decode("utf-8","replace")
    p=Parser();p.feed(html)
    rows=[];seen=set()
    for region,pref,name in p.items:
        key=(region,pref,name)
        if key in seen:continue
        seen.add(key)
        rows.append((region,pref,name,URL,datetime.now(timezone.utc).isoformat(),"unverified_directory_candidate"))
    if len(rows)<300:raise RuntimeError(f"Only {len(rows)} candidates parsed; refusing to overwrite data")
    out=Path(__file__).resolve().parents[1]/"data"/"directory_candidates.csv"
    with out.open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f);w.writerow(["region","prefecture_heading","resort_name","source_url","retrieved_at_utc","verification_status"]);w.writerows(rows)
    print(f"Saved {len(rows)} directory candidates, not an authoritative operating-resort count")
if __name__=="__main__":main()
