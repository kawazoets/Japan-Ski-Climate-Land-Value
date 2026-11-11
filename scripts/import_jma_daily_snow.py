"""Import user-downloaded JMA daily snow-depth CSV with strict data-quality handling.

JMA obsdl exports have multirow headers and quality/homogeneity fields.
Do not silently interpret missing values as zero, or assume a single header row.
Usage: python scripts/import_jma_daily_snow.py path/to/obsdl.csv STATION_ID
"""
import csv,datetime,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 if len(sys.argv)!=3:raise SystemExit("Usage: import_jma_daily_snow.py JMA_CSV STATION_ID")
 path=Path(sys.argv[1]);station=sys.argv[2]
 if not station.isdigit():raise SystemExit("Station ID must be numeric")
 raw=path.read_bytes()
 for encoding in ("cp932","utf-8-sig"):
  try:lines=raw.decode(encoding).splitlines();break
  except UnicodeDecodeError:continue
 else:raise SystemExit("Unknown CSV encoding")
 rows=list(csv.reader(lines))
 header_idx=next((i for i,r in enumerate(rows) if r and r[0].strip() in ("年月日","日付")),None)
 if header_idx is None:raise SystemExit("JMA date header not found; inspect CSV format")
 header=rows[header_idx]
 dates=[];data=[]
 for row in rows[header_idx+1:]:
  if not row:continue
  date=row[0].strip()
  try:d=datetime.date.fromisoformat(date.replace("/","-"))
  except ValueError:continue
  if not 2016<=d.year<=2026:continue
  dates.append((d,row))
 if not dates:raise SystemExit("No observations 2016–2026")
 # Only accept unambiguous single-station, single-depth-value exports.
 depth_cols=[i for i,h in enumerate(header) if "日最深積雪" in h and "品質" not in h and "均質" not in h]
 if len(depth_cols)!=1:raise SystemExit("Ambiguous JMA depth columns; must select one station and one variable: "+str(depth_cols))
 i=depth_cols[0]
 for d,row in dates:
  if i>=len(row):raise SystemExit("Truncated row "+str(d))
  value=row[i].strip()
  if value in ("","///","×","--","-"):depth=""
  else:
   try:depth=float(value)
   except ValueError:raise SystemExit("Non-numeric snow depth "+str((d,value)))
   if depth<0 or depth>1500:raise SystemExit("Out-of-range depth "+str((d,depth)))
  data.append([station,d.isoformat(),depth,"JMA obsdl",path.name])
 target=ROOT/"data/jma_daily_snow_depth_2016_2026.csv"
 target.parent.mkdir(parents=True,exist_ok=True)
 existing=[]
 if target.exists():
  with target.open(encoding="utf-8",newline="") as f:existing=list(csv.DictReader(f))
 keys={(r["station_id"],r["date"]) for r in existing}
 if any((station,row[1]) in keys for row in data):raise SystemExit("Duplicate station-day: refusing overwrite")
 with target.open("a",encoding="utf-8",newline="") as f:
  w=csv.writer(f)
  if not existing:w.writerow(["station_id","date","snow_depth_cm","source","source_filename"])
  w.writerows(data)
 print("Imported",len(data),"daily JMA rows for station",station,"missing",sum(x[2]=="" for x in data))
if __name__=="__main__":main()
