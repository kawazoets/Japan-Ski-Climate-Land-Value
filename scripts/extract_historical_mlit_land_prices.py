"""Extract annual 2016–2025 prices from official MLIT L01-25 shapefile ZIP.

Run after downloading L01-25_GML.zip from the official MLIT website.
Zero means the site was not selected in that year, not a zero price.
"""
import csv,zipfile,io,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIELDS=["source_year","point_id","latitude","longitude","year","price_jpy_per_sqm","municipality_code","land_use_code","source_file"]
def main():
 source=ROOT/"data/raw/L01-25_GML.zip"
 if not source.exists():raise SystemExit("Official L01-25_GML.zip not downloaded; no data fabricated")
 try:import shapefile
 except ImportError:raise SystemExit("Install pyshp: pip install pyshp")
 with zipfile.ZipFile(source) as z:
  names=z.namelist();shps=[n for n in names if n.lower().endswith(".shp")]
  if not shps:raise SystemExit("No shapefile in official archive")
  out=[]
  for shp in shps:
   base=shp[:-4];dbf=next((n for n in names if n.lower()==(base+".dbf").lower()),None)
   if not dbf:continue
   shx=next((n for n in names if n.lower()==(base+".shx").lower()),None)
   reader=shapefile.Reader(shp=io.BytesIO(z.read(shp)),dbf=io.BytesIO(z.read(dbf)),**({"shx":io.BytesIO(z.read(shx))} if shx else {}))
   fields=[f[0] for f in reader.fields[1:]]
   if "L01_104" not in fields:raise SystemExit("Unexpected schema: missing 2025 annual price field")
   for i,rec in enumerate(reader.iterShapeRecords()):
    d=dict(zip(fields,rec.record))
    shape=rec.shape
    if not shape.points:continue
    lon,lat=shape.points[0][:2]
    if not 20<=lat<=47 or not 122<=lon<=154:raise SystemExit("Unexpected coordinate order")
    for year in range(2016,2026):
     field="L01_104" if year==2025 else "L01_%03d"%(year-1921)
     if field not in d:raise SystemExit("Missing annual price field "+field)
     try:price=int(float(d[field] or 0))
     except (ValueError,TypeError):raise SystemExit("Non-numeric price")
     if price<=0:continue
     out.append([2025,f"{base}:{i}",lat,lon,year,price,d.get("L01_001",""),d.get("L01_002",""),"L01-25_GML.zip"])
 target=ROOT/"data/historical_mlit_land_price_points_2016_2025.csv"
 with target.open("w",encoding="utf-8",newline="") as f:
  w=csv.writer(f);w.writerow(FIELDS);w.writerows(out)
 print("Extracted",len(out),"official year-point observations into",target)
if __name__=="__main__":main()
