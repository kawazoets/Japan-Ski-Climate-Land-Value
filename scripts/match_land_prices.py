"""Match verified resort coordinates to land-price observations (haversine).
Input data must be independently verified; empty tables produce empty output.
"""
import csv, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"data"
def read(name):
    with (ROOT/name).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def km(a,b,c,d):
    r=6371.0088
    x,y=math.radians(float(c)-float(a)),math.radians(float(d)-float(b))
    q=math.sin(x/2)**2+math.cos(math.radians(float(a)))*math.cos(math.radians(float(c)))*math.sin(y/2)**2
    return 2*r*math.asin(min(1,math.sqrt(q)))
def main():
    resorts=read("resorts.csv");prices=read("land_prices.csv")
    rows=[]
    for resort in resorts:
        if not resort.get("latitude") or not resort.get("longitude"):continue
        candidates=[]
        for p in prices:
            if not p.get("latitude") or not p.get("longitude"):continue
            distance=km(resort["latitude"],resort["longitude"],p["latitude"],p["longitude"])
            if distance<=20:candidates.append((distance,p))
        for distance,p in sorted(candidates,key=lambda x:x[0]):
            rows.append([resort["resort_id"],p["point_id"],p["year"],round(distance,3),p["land_use"],p["price_jpy_m2"]])
    with (ROOT/"resort_land_matches.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f);w.writerow(["resort_id","point_id","year","distance_km","land_use","price_jpy_m2"]);w.writerows(rows)
    print(f"Matched {len(rows)} resort-point-year pairs within 20km. No causal inference.")
if __name__=="__main__":main()
