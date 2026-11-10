"""Join verified ski-area coordinates with official MLIT 2026 land-price points.

Input resort coordinates must be explicitly verified. Unverified names are NOT geocoded.
Input land prices must be extracted from the official 2026 MLIT archive.
"""
import csv,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RESORTS=ROOT/"data/resort_coordinates_verified.csv"
POINTS=ROOT/"data/mlit_2026_all_points.csv"
OUT=ROOT/"data/resort_nearest_land_points.csv"
def dist(a,b,c,d):
    p1,p2=math.radians(a),math.radians(c)
    dp=math.radians(c-a);dl=math.radians(d-b)
    h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 6371*2*math.asin(min(1,math.sqrt(h)))
def main():
    if not RESORTS.exists():raise SystemExit(f"Verified resort coordinates not yet available: {RESORTS}")
    if not POINTS.exists():raise SystemExit(f"Land-price CSV not yet available: {POINTS}")
    with RESORTS.open(encoding="utf-8",newline="") as f:resorts=list(csv.DictReader(f))
    if not resorts:raise SystemExit("No verified resort coordinates")
    with POINTS.open(encoding="utf-8",newline="") as f:
        rd=csv.DictReader(f)
        points=[]
        for p in rd:
            try:points.append((float(p["latitude"]),float(p["longitude"]),p))
            except (ValueError,KeyError):continue
    if not points:raise SystemExit("No valid MLIT point coordinates")
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w",encoding="utf-8",newline="") as f:
        fields=["resort_name","resort_latitude","resort_longitude","land_point_latitude","land_point_longitude","distance_km","land_price_2026_raw_L01_008","land_point_municipality_L01_001","source"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for resort in resorts:
            a=float(resort["latitude"]);b=float(resort["longitude"])
            nearby=sorted(((dist(a,b,lat,lon),lat,lon,p) for lat,lon,p in points if abs(lat-a)<0.4 and abs(lon-b)<0.6),key=lambda x:x[0])[:5]
            for d,lat,lon,p in nearby:
                w.writerow({"resort_name":resort["resort_name"],"resort_latitude":a,"resort_longitude":b,"land_point_latitude":lat,"land_point_longitude":lon,"distance_km":round(d,3),"land_price_2026_raw_L01_008":p.get("L01_008",""),"land_point_municipality_L01_001":p.get("L01_001",""),"source":"MLIT L01-26_GML.zip"})
    print("Saved nearest-point candidates:",OUT)
if __name__=="__main__":main()
