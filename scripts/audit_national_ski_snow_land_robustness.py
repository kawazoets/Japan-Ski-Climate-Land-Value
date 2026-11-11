"""Robustness audit for exploratory snow-versus-land-price associations.

Station-cluster de-duplication, urban appreciation exclusions, Pearson and
Spearman, and leave-one-out ranges. All descriptive; no causal interpretation.
"""
import csv,math,statistics,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/"data/ski_snow_land_exploratory_matched_2016_2026.csv").open(encoding="utf-8-sig",newline="") as f:records=list(csv.DictReader(f))
def pearson(x,y):
 if len(x)<3:return None
 a=statistics.mean(x);b=statistics.mean(y)
 den=math.sqrt(sum((v-a)**2 for v in x)*sum((v-b)**2 for v in y))
 return sum((v-a)*(w-b) for v,w in zip(x,y))/den if den else None
def rank(vals):
 order=sorted(range(len(vals)),key=lambda i:vals[i]);out=[0.0]*len(vals);k=0
 while k<len(vals):
  j=k+1
  while j<len(vals) and vals[order[j]]==vals[order[k]]:j+=1
  for idx in order[k:j]:out[idx]=(k+j-1)/2+1
  k=j
 return out
def describe(rs,key):
 x=[float(r[key]) for r in rs];y=[float(r["land_median_change_2016_2026_pct"]) for r in rs]
 p=pearson(x,y);s=pearson(rank(x),rank(y))
 loo=[pearson(x[:i]+x[i+1:],y[:i]+y[i+1:]) for i in range(len(x))] if len(x)>3 else []
 loo=[v for v in loo if v is not None]
 return len(rs),p,s,(min(loo),max(loo)) if loo else None
def fmt(v):return "n/a" if v is None else f"{v:+.3f}"
lines=["# Sensitivity of nationwide snow trend versus land-price correlations","",
"**Descriptive associations only. Snow station coverage is not ski-resort operating duration.**","",
"| Radius | Sample definition | N | Pearson r (30cm snow days) | Spearman rho | Leave-one-resort-out Pearson range |",
"|---|---|---:|---:|---:|---|"]
for radius in (10,20):
 base=[r for r in records if int(r["land_radius_km"])==radius]
 sets=[("All eligible resorts",base),
 ("Exclude >=50% land appreciation",[r for r in base if float(r["land_median_change_2016_2026_pct"])<50]),
 ("Exclude >=30% land appreciation",[r for r in base if float(r["land_median_change_2016_2026_pct"])<30]),
 ("At least 20 matched land points",[r for r in base if int(r["land_matched_point_count"])>=20])]
 unique={}
 for r in sorted(base,key=lambda r:(-int(r["land_matched_point_count"]),r["candidate_id"])):
  unique.setdefault(r["station_id"],r)
 sets.append(("One resort per JMA station (max land points)",list(unique.values())))
 for label,rs in sets:
  n,p,s,lo=describe(rs,"snow_30cm_days_trend_per_year")
  bounds=f"{fmt(lo[0])} to {fmt(lo[1])}" if lo else "n/a"
  lines.append(f"| {radius} km | {label} | {n} | {fmt(p)} | {fmt(s)} | {bounds} |")
lines+=["","## Interpretation rules","",
"- A sign change under simple exclusions indicates instability, not a reliable association.",
"- Resort observations sharing JMA stations or overlapping MLIT buffers are not independent.",
"- 2016–2026 land changes are a single endpoint difference, while snow trends are based on ten winters.",
"- Urban proximity, property type, ski-area elevation, and resort operation status are uncontrolled.",
"- Land-point survival to 2026 creates selection bias; no inference about closed resorts or missing points.",
"- Spearman rank correlation reduces sensitivity to extreme percentage changes but cannot correct confounding.",
""]
report=ROOT/"reports/national_ski_snow_land_robustness.md"
report.write_text("\n".join(lines),encoding="utf-8")
print(report.read_text())
