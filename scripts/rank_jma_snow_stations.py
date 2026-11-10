"""Rank nearby JMA snow-observation stations for 13 ski areas.

JMA official master is CP932 and gives degree + decimal minutes. Distances
are great-circle; station suitability must be reviewed, never auto-verified.
"""
import csv,io,math,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL="https://www.jma.go.jp/jma/kishou/know/amedas/snow_master.zip"
SOURCE=ROOT/"data/jma_station_verification_queue.csv"
OUTPUT=ROOT/"data/jma_nearest_snow_stations.csv"
def haversine(a,b,c,d):
    a,b,c,d=map(math.radians,(a,b,c,d))
    x=math.sin((c-a)/2)**2+math.cos(a)*math.cos(c)*math.sin((d-b)/2)**2
    return 12742*math.asin(min(1,math.sqrt(x)))
def coord(r,deg,minute):
    return float(r[deg])+float(r[minute])/60
def main():
    with SOURCE.open(encoding="utf-8-sig",newline="") as f:resorts=list(csv.DictReader(f))
    req=urllib.request.Request(URL,headers={"User-Agent":"JapanSkiClimateLandValue/1.0"})
    with urllib.request.urlopen(req,timeout=45) as response:blob=response.read(5_000_001)
    if len(blob)>5_000_000:raise SystemExit("Unexpected master size")
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        name=next(n for n in z.namelist() if n.lower().endswith(".csv"))
        stations=list(csv.DictReader(io.StringIO(z.read(name).decode("cp932"))))
    points=[]
    for s in stations:
        try:
            lat=coord(s,"緯度(度)","緯度(分)")
            lon=coord(s,"経度(度)","経度(分)")
        except (ValueError,TypeError,KeyError):continue
        points.append((lat,lon,s))
    if len(points)<250:raise SystemExit(f"Unexpectedly few JMA stations: {len(points)}")
    output=[]
    for resort in resorts:
        a=float(resort["resort_latitude"]);b=float(resort["resort_longitude"])
        nearest=sorted(((haversine(a,b,lat,lon),lat,lon,s) for lat,lon,s in points),key=lambda t:t[0])[:5]
        for rank,(km,lat,lon,s) in enumerate(nearest,1):
            output.append({"resort_name":resort["resort_name"],"resort_latitude":a,"resort_longitude":b,"station_rank":rank,"jma_station_id":s["観測所番号"],"jma_station_name":s["観測所名"],"jma_station_region":s["都府県振興局"],"jma_station_address":s["所在地"],"jma_station_type":s["種類"],"jma_station_latitude":round(lat,6),"jma_station_longitude":round(lon,6),"jma_station_altitude_m":s["海面上の高さ(ｍ)"],"straight_line_distance_km":round(km,3),"station_suitability":"unverified_candidate","snow_observation_2016_2026":"not_checked","source_url":URL})
    OUTPUT.parent.mkdir(exist_ok=True)
    with OUTPUT.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(output[0]));w.writeheader();w.writerows(output)
    print(f"JMA stations={len(points)}; ski areas={len(resorts)}; ranked candidates={len(output)}")
if __name__=="__main__":main()
