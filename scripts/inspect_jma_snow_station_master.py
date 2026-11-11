"""Inventory the official JMA snow observation station master and match ski resorts.

Download source: https://www.jma.go.jp/jma/kishou/know/amedas/snow_master.zip
Keep unknown schemas as explicit diagnostics; never fabricate station coordinates.
"""
import csv,io,zipfile,urllib.request,re,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL="https://www.jma.go.jp/jma/kishou/know/amedas/snow_master.zip"
def main():
 req=urllib.request.Request(URL,headers={"User-Agent":"Japan-Ski-Climate-Land-Value/1.0 research"})
 with urllib.request.urlopen(req,timeout=45) as response:raw=response.read()
 if not zipfile.is_zipfile(io.BytesIO(raw)):raise SystemExit("Official response not a ZIP")
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  names=z.namelist()
  report=["# Official JMA snow station master inventory","",f"Source: {URL}","",f"ZIP size: {len(raw)} bytes","", "## ZIP members",""]
  for name in names:
   if name.endswith("/"):continue
   b=z.read(name)
   report.append(f"- `{name}`: {len(b)} bytes")
   if name.lower().endswith((".csv",".txt")):
    for enc in ("utf-8-sig","cp932","shift_jis"):
     try:t=b.decode(enc);break
     except UnicodeDecodeError:continue
    else:
     report.append("  - No supported text encoding");continue
    lines=t.splitlines()
    report.append(f"  - encoding: {enc}, lines: {len(lines)}")
    report.append("  - first 4 lines (truncated):")
    for line in lines[:4]:report.append("    - "+line[:350].replace("|","/"))
 target=ROOT/"reports/jma_official_snow_station_master_inventory.md"
 target.parent.mkdir(exist_ok=True)
 target.write_text("\n".join(report)+"\n",encoding="utf-8")
 print(target.read_text())
if __name__=="__main__":main()
