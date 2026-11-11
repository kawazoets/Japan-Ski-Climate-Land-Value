"""Extract official 2026 MLIT L01 nationwide point history (2016–2026).

Verified against L01-26_GML.zip DBF: annual prices L01_095..L01_105;
L01_001 municipality, L01_025 address, L01_028 land use.
"""
import csv,io,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIELDS=["point_id_2026","municipality_code","address_2026","land_use_2026","latitude","longitude","year","price_jpy_per_sqm","source"]
def main():
 source=ROOT/"data/raw/L01-26_GML.zip"
 if not source.exists():raise SystemExit("Place official L01-26_GML.zip in data/raw/")
 try:import shapefile
 except ImportError:raise SystemExit("pip install pyshp")
 out=[]
 with zipfile.ZipFile(source) as z:
  prefix=next((x[:-4] for x in z.namelist() if x.lower().endswith(".shp")),None)
  if prefix is None:raise SystemExit("No shapefile")
  r=shapefile.Reader(shp=io.BytesIO(z.read(prefix+".shp")),dbf=io.BytesIO(z.read(prefix+".dbf")),encoding="cp932")
  fields=[x[0] for x in r.fields[1:]]
  required={"L01_001","L01_025","L01_028"}|{"L01_%03d"%i for i in range(95,106)}
  if not required.issubset(fields):raise SystemExit("Unexpected MLIT schema: "+str(sorted(required-set(fields))))
  for i,rec in enumerate(r.iterShapeRecords(),1):
   d=dict(zip(fields,rec.record))
   if len(rec.shape.points)!=1:raise SystemExit("Unexpected non-point geometry")
   lon,lat=rec.shape.points[0]
   if not (20<=lat<=47 and 122<=lon<=154):raise SystemExit("Invalid lat/lon")
   for year in range(2016,2027):
    value=d["L01_%03d"%(year-1921)]
    if value in (None,"",0,"0"):continue
    price=int(value)
    if price<=0:continue
    out.append([f"L01-26-{i:05d}",str(d["L01_001"]),str(d["L01_025"]),str(d["L01_028"]),f"{lat:.8f}",f"{lon:.8f}",year,price,"MLIT L01-26_GML.zip"])
 target=ROOT/"data/MLIT_land_prices_2016_2026.csv"
 target.parent.mkdir(parents=True,exist_ok=True)
 with target.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f);w.writerow(FIELDS);w.writerows(out)
 if len(out)<250000:raise SystemExit("Unexpectedly few records "+str(len(out)))
 print("Official point-year observations:",len(out),"output:",target)
if __name__=="__main__":main()
