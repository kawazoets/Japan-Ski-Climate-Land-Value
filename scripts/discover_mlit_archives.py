"""Discover official MLIT land-price ZIP links and write a provenance manifest.

No automated GitHub workflow or email notifications. Run manually when needed.
"""
import csv
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

PAGE = "https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-L01-2026.html"
OUT = Path(__file__).resolve().parents[1] / "data" / "mlit_land_price_archive_manifest.csv"
class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag!="a":return
        d=dict(attrs)
        href=d.get("href","")
        if href:self.links.append(href)

def main():
    req=urllib.request.Request(PAGE,headers={"User-Agent":"JapanSkiClimateLandValueResearch/1.0"})
    with urllib.request.urlopen(req,timeout=30) as response:
        html=response.read().decode("utf-8",errors="replace")
    p=Links();p.feed(html)
    records={}
    for href in p.links:
        url=urllib.parse.urljoin(PAGE,href)
        m=re.search(r"L01-(\d{2})_GML\.zip(?:\?|$)",url,re.I)
        if not m:continue
        year=2000+int(m.group(1))
        records[year]={"year":year,"archive_filename":f"L01-{m.group(1)}_GML.zip","archive_url":url,"source_page":PAGE,"verification_status":"link_discovered_not_downloaded"}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["year","archive_filename","archive_url","source_page","verification_status"])
        w.writeheader();w.writerows(records[y] for y in sorted(records))
    print(f"Discovered {len(records)} direct archive links; manifest: {OUT}")
    if not records:
        print("No direct ZIP links found in HTML; the website may use scripted downloads. No URLs were invented.")
if __name__=="__main__":main()
