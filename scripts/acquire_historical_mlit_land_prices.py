"""Acquire historical MLIT L01 land-price ZIP from the official download listing.

Obtain the official 2026 data for longitudinal linkage; validate historical fields before use.
Never fabricate a ZIP URL: discover and validate an official download link.
"""
import argparse,html.parser,re,urllib.request,urllib.parse,zipfile,io,csv
from pathlib import Path
PAGE="https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-L01-2026.html"
ROOT=Path(__file__).resolve().parents[1]
class Links(html.parser.HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  for k in ("href","data-url","data-href"):
   if a.get(k):self.urls.append(a[k])
def discover():
 req=urllib.request.Request(PAGE,headers={"User-Agent":"Mozilla/5.0 (historical academic research)"})
 with urllib.request.urlopen(req,timeout=45) as f:body=f.read().decode("utf-8","replace")
 p=Links();p.feed(body)
 matches=[urllib.parse.urljoin(PAGE,u) for u in p.urls if re.search(r"L01-26_GML\.zip",u,re.I)]
 return list(dict.fromkeys(matches))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--discover-only",action="store_true");args=ap.parse_args()
 urls=discover()
 out=ROOT/"reports/historical_mlit_land_price_acquisition.md"
 if not urls:
  out.write_text("# Historical MLIT land-price acquisition\n\nOfficial listing: "+PAGE+"\n\nThe 2026 L01 nationwide ZIP is listed but no direct download URL was exposed in static anchor attributes. Do not invent URLs. Obtain the official link via the site's supported download interface.\n",encoding="utf-8")
  raise SystemExit("No official direct download link exposed; see report")
 if args.discover_only:
  out.write_text("# Historical MLIT land-price acquisition\n\nOfficial listing: "+PAGE+"\n\nDiscovered ZIP links:\n"+"\n".join("- "+x for x in urls)+"\n",encoding="utf-8")
  print("Discovered",len(urls),"candidate links");return
 url=urls[0]
 if urllib.parse.urlparse(url).hostname not in ("nlftp.mlit.go.jp","www.nlftp.mlit.go.jp","ksj-api.mlit.go.jp"):raise SystemExit("Unexpected ZIP host")
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
 with urllib.request.urlopen(req,timeout=120) as f:data=f.read(60_000_001)
 if len(data)>60_000_000:raise SystemExit("Unexpected ZIP size")
 z=zipfile.ZipFile(io.BytesIO(data));members=z.namelist()
 out.write_text("# Historical MLIT land-price acquisition\n\nOfficial listing: "+PAGE+"\n\nDownload: "+url+"\n\nZIP bytes: "+str(len(data))+"\n\nMembers: "+"; ".join(members[:30])+"\n\nAnnual historic price attributes must be decoded from the 2026 SHP/GML schema; this ZIP acquisition does not by itself constitute a validated land-price panel.\n",encoding="utf-8")
 (ROOT/"data/raw").mkdir(parents=True,exist_ok=True)
 (ROOT/"data/raw/L01-26_GML.zip").write_bytes(data)
 print("Saved",len(data),"bytes of official 2026 MLIT L01 land-price data")
if __name__=="__main__":main()
