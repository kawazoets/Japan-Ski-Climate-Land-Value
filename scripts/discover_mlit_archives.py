"""Discover MLIT L01 archives from official HTML and STAC metadata.

A discovery with zero download URLs is an error, not a success.
"""
import csv,json,re,urllib.request,urllib.parse
from html.parser import HTMLParser
from pathlib import Path
PAGE="https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-L01-2026.html"
STAC="https://stac.yuiseki.net/mlit-nlftp/collections/L01/items/L01-26_GML.json"
OUT=Path(__file__).resolve().parents[1]/"data/mlit_land_price_archive_manifest.csv"
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=="a" and d.get("href"):self.links.append(d["href"])
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; academic land-price research)"})
    with urllib.request.urlopen(req,timeout=35) as response:return response.read()
def main():
    found={}
    errors=[]
    try:
        raw=fetch(PAGE).decode("utf-8",errors="replace")
        p=Links();p.feed(raw)
        for href in p.links:
            url=urllib.parse.urljoin(PAGE,href)
            m=re.search(r"L01-(\d{2})_GML\.zip(?:\?|$)",url,re.I)
            if m:
                year=2000+int(m.group(1))
                found[year]=(url,"official_page_anchor")
        print(f"Official page: {len(found)} direct archive links")
    except Exception as exc:errors.append(f"Official page: {exc}")
    # STAC metadata is a discovery fallback; ZIP asset href is retained unchanged.
    if 2026 not in found:
        try:
            obj=json.loads(fetch(STAC))
            for asset in obj.get("assets",{}).values():
                href=asset.get("href","")
                if re.search(r"L01-26_GML\.zip(?:\?|$)",href,re.I):
                    found[2026]=(urllib.parse.urljoin(STAC,href),"third_party_stac_asset")
                    break
            print("STAC asset found:",2026 in found)
        except Exception as exc:errors.append(f"STAC: {exc}")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["year","archive_filename","archive_url","discovery_source","source_page","verification_status"])
        w.writeheader()
        for year,(url,method) in sorted(found.items()):
            w.writerow({"year":year,"archive_filename":f"L01-{year%100:02d}_GML.zip","archive_url":url,"discovery_source":method,"source_page":PAGE,"verification_status":"discovered_not_downloaded"})
    print(f"Found {len(found)} links; manifest {OUT}")
    for error in errors:print("Warning:",error)
    if not found:raise SystemExit("ERROR: no archive URLs found. Do not mark collection successful.")
if __name__=="__main__":main()
