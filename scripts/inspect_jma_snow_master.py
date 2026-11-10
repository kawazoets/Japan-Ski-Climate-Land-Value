"""Download and inventory the official JMA snow-station master ZIP.

The master is station *metadata*, not daily snow observations. Preserve the
original ZIP and inspect member encodings/headers before building a join.
"""
import csv,hashlib,io,json,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL="https://www.jma.go.jp/jma/kishou/know/amedas/snow_master.zip"
OUT=ROOT/"reports/jma_snow_station_master_inventory.json"
def main():
    req=urllib.request.Request(URL,headers={"User-Agent":"JapanSkiClimateLandValue/1.0 (research; single request)"})
    with urllib.request.urlopen(req,timeout=45) as response:
        blob=response.read(5_000_001)
    if len(blob)>5_000_000:raise SystemExit("Unexpectedly large JMA station master")
    inventory={"source_url":URL,"sha256":hashlib.sha256(blob).hexdigest(),"archive_bytes":len(blob),"files":[]}
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for member in z.infolist():
            if member.is_dir():continue
            data=z.read(member)
            record={"filename":member.filename,"size_bytes":len(data)}
            if member.filename.lower().endswith((".csv",".txt",".index")):
                for encoding in ("utf-8-sig","cp932","shift_jis"):
                    try:content=data.decode(encoding);record["encoding"]=encoding;break
                    except UnicodeDecodeError:continue
                else:record["encoding"]="unrecognized";inventory["files"].append(record);continue
                lines=content.splitlines()
                record["line_count"]=len(lines)
                record["first_three_lines"]=[line[:600] for line in lines[:3]]
                try:
                    reader=csv.reader(lines)
                    record["first_row_fields"]=next(reader,[])
                except csv.Error:record["first_row_fields"]=[]
            inventory["files"].append(record)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Inspected {len(inventory['files'])} files from official JMA snow station master; {len(blob)} bytes")
if __name__=="__main__":main()
