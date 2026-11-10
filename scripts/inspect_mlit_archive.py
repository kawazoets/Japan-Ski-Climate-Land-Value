"""Download and inspect the official 2026 MLIT land-price GML archive.

Manual-only; saves a compact inspection report, not a large ZIP in Git.
"""
import csv,hashlib,json,re,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/"data/mlit_land_price_archive_manifest.csv"
out=ROOT/"reports/mlit_archive_inspection.json"
with manifest.open(encoding="utf-8",newline="") as f:
    records=list(csv.DictReader(f))
selected=next((r for r in records if r["year"]=="2026"),None)
if not selected:raise SystemExit("Missing 2026 archive URL in manifest")
url=selected["archive_url"]
if not url.startswith("https://nlftp.mlit.go.jp/ksj/"):raise SystemExit("Untrusted download host")
target=Path("/tmp/L01-26_GML.zip")
request=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
try:
    with urllib.request.urlopen(request,timeout=90) as response, target.open("wb") as f:
        total=0
        while True:
            chunk=response.read(1024*1024)
            if not chunk:break
            total+=len(chunk)
            if total>120*1024*1024:raise RuntimeError("Archive exceeds safety limit")
            f.write(chunk)
except Exception as exc:
    raise SystemExit(f"Archive download failed: {exc}")
if not zipfile.is_zipfile(target):raise SystemExit("Downloaded file is not a ZIP archive")
with zipfile.ZipFile(target) as z:
    members=[{"name":i.filename,"bytes_uncompressed":i.file_size} for i in z.infolist()]
    if sum(x["bytes_uncompressed"] for x in members)>1000*1024*1024:raise SystemExit("Archive uncompressed size exceeds safety limit")
result={"archive_url":url,"archive_bytes":target.stat().st_size,"sha256":hashlib.file_digest(target.open("rb"),"sha256").hexdigest(),"member_count":len(members),"members":members[:150],"data_status":"downloaded_and_zip_verified_not_yet_parsed"}
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Verified archive:",result["archive_bytes"],"bytes,",len(members),"members")
