"""Summarize observed 1996–2026 MLIT land-price histories without causal claims."""
import csv,collections,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/"data/mlit_landprice_historical_panel_1983_2026.csv"
out=ROOT/"data/mlit_1996_2026_municipality_observed_panel.csv"
groups=collections.defaultdict(list)
with source.open(encoding="utf-8",newline="") as f:
 for r in csv.DictReader(f):
  year=int(r["year"])
  if 1996<=year<=2026:
   try: price=float(r["price_yen_m2"])
   except (ValueError,TypeError):continue
   if price>0:groups[(r["municipality_code"],year)].append(price)
with out.open("w",encoding="utf-8",newline="") as f:
 w=csv.writer(f);w.writerow(["municipality_code","year","observed_point_count","median_yen_m2","mean_yen_m2","cohort_note"])
 for (municipality,year),prices in sorted(groups.items()):
  w.writerow([municipality,year,len(prices),round(statistics.median(prices),2),round(statistics.mean(prices),2),"2026-surviving-site historical sample; not representative market index"])
years=collections.Counter()
for (_,year),prices in groups.items():years[year]+=len(prices)
missing=[year for year in range(1996,2027) if years[year]==0]
report=ROOT/"reports/mlit_1996_2026_coverage.md"
report.write_text("# MLIT 1996–2026 observed historical land-price coverage\n\n"+
 "**These observations are not yet a ski-resort climate impact analysis.**\n\n"+
 f"- Municipality-year groups: {len(groups)}\n- Missing years: {missing}\n"+
 "- Historical annual prices are linked to surviving 2026 observation points; missing/closed points are not recovered.\n"+
 "- Municipality medians mix land-use categories and may shift with the point composition. Do not interpret as representative price indices.\n"+
 "- Before using as the research outcome, match each observation to validated ski-resort geography, land-use type and fixed-site cohorts; control for confounding.\n\n"+
 "| Year | Positive-price point-years |\n|---|---:|\n"+
 "".join(f"| {year} | {years[year]} |\n" for year in range(1996,2027)),encoding="utf-8")
if missing:raise SystemExit(f"Missing historical land-price years: {missing}")
print(f"1996–2026 coverage: {sum(years.values())} point-years across {len(groups)} municipality-years")
