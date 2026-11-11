"""Inspect JMA synoptic station daily_s1 snow column and HTML table structure."""
import urllib.request
from bs4 import BeautifulSoup
from pathlib import Path
cases=[("札幌","14","47412"),("旭川","12","47407"),("倶知安","16","47433")]
lines=["# JMA synoptic stations: official daily_s1 snow-table inspection",""]
for name,prec,block in cases:
 url=f"https://www.data.jma.go.jp/stats/etrn/view/daily_s1.php?prec_no={prec}&block_no={block}&year=2025&month=1&day=&view=p2"
 lines.extend([f"## {name}",f"- URL: {url}"])
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
  with urllib.request.urlopen(req,timeout=30) as f:html=f.read()
  soup=BeautifulSoup(html,"html.parser")
  lines.append(f"- Station name present: {name in soup.get_text(' ',strip=True)}")
  for table in soup.select("table")[:10]:
   txt=table.get_text(" ",strip=True)
   if "積雪" not in txt:continue
   lines.append("- Table ID: "+str(table.get("id")))
   for tr in table.select("tr")[:8]:
    lines.append("  - "+repr([c.get_text(" ",strip=True)[:60] for c in tr.find_all(["th","td"],recursive=False)])[:1200])
 except Exception as e:lines.append(f"- ERROR: {type(e).__name__}: {e}")
out=Path(__file__).resolve().parents[1]/"reports/jma_synoptic_snow_table_diagnostics.md"
out.write_text("\n".join(lines)+"\n",encoding="utf-8")
print(out.read_text())
