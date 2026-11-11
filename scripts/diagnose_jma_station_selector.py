"""Inspect JMA prefecture station-selection page source and linked JS metadata."""
import urllib.request,re,html
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
urls=["https://www.data.jma.go.jp/stats/etrn/select/prefecture.php?prec_no=12","https://www.data.jma.go.jp/stats/etrn/select/prefecture00.php?prec_no=12"]
out=["# JMA station selector source inspection",""]
for url in urls:
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
  with urllib.request.urlopen(req,timeout=30) as f:body=f.read().decode("utf-8","replace")
  soup=BeautifulSoup(body,"html.parser")
  out.extend([f"## {url}",f"- HTML length: {len(body)}","- Script sources:"])
  for s in soup.select("script[src]"):out.append("  - "+s["src"])
  out.append("- Relevant lines:")
  for line in body.splitlines():
   if re.search("block_no|prec_no|station|amedas|point|観測所|地点",line,re.I):
    out.append("  - "+html.escape(line.strip()[:350]))
    if len(out)>130:break
 except Exception as e:out.append(f"- ERROR: {e}")
target=ROOT/"reports/jma_station_selector_html_diagnostics.md"
target.write_text("\n".join(out)+"\n",encoding="utf-8")
print(target.read_text()[:8000])
