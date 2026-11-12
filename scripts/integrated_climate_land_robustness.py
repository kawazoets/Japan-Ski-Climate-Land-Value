"""Reproduce spatial overlap and model robustness from existing source CSVs. No API calls."""
import csv,math,statistics
from collections import defaultdict
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def read(p):
 with (P/p).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
land=read("data/ski_resort_observed_land_price_1996_2026.csv")
clim=read("data/ski_region_reanalysis_climate_1986_2025.csv")
loc={r["candidate_id"]:r for r in read("data/national_resort_osm_reconciliation.csv")}
annual=defaultdict(dict)
for r in clim:
 if r["mean_temperature_c"] and r["winter_snowfall_cm"]:
  annual[r["candidate_id"]][int(r["year"])]=(float(r["mean_temperature_c"]),float(r["winter_snowfall_cm"]))
def slope(a):
 xs=[v[0] for v in a];ys=[v[1] for v in a];mx=statistics.mean(xs);my=statistics.mean(ys)
 return 10*sum((x-mx)*(y-my) for x,y in a)/sum((x-mx)**2 for x in xs)
def pearson(x,y):
 if len(x)<3:return float("nan")
 mx=statistics.mean(x);my=statistics.mean(y)
 den=math.sqrt(sum((v-mx)**2 for v in x)*sum((v-my)**2 for v in y))
 return sum((a-mx)*(b-my) for a,b in zip(x,y))/den if den else float("nan")
regions={}
for r in land:
 if r["radius_km"]=="10" and r["year"]=="2026" and r["median_same_point_change_pct"] and int(r["matched_1996_2026_point_count"] or 0)>=5:
  cid=r["candidate_id"]
  if cid not in loc:continue
  years=annual.get(cid,{})
  if len(years)<30:continue
  try:lat=float(loc[cid]["latitude_candidate"]);lon=float(loc[cid]["longitude_candidate"])
  except (TypeError,ValueError):continue
  regions[cid]={"name":r["resort_name"],"price":float(r["median_same_point_change_pct"]),"temp":slope([(y,v[0]) for y,v in years.items()]),"snow":slope([(y,v[1]) for y,v in years.items()]),"n":int(r["matched_1996_2026_point_count"]),"lat":lat,"lon":lon,"coverage":len(years)}
data=list(regions.values())
def corr(d,key):return pearson([r["price"] for r in d],[r[key] for r in d])
def distance(a,b):
 la1,la2=math.radians(a["lat"]),math.radians(b["lat"])
 dl=la1-la2;dn=math.radians(a["lon"]-b["lon"])
 h=math.sin(dl/2)**2+math.cos(la1)*math.cos(la2)*math.sin(dn/2)**2
 return 12742*math.asin(math.sqrt(h))
def clusters(km):
 parent=list(range(len(data)))
 def root(i):
  while parent[i]!=i:
   parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i in range(len(data)):
  for j in range(i+1,len(data)):
   if distance(data[i],data[j])<=km:parent[root(j)]=root(i)
 groups=defaultdict(list)
 for i,r in enumerate(data):groups[root(i)].append(r)
 return list(groups.values())
def solve(a,b):
 n=len(b);m=[list(a[i])+[b[i]] for i in range(n)]
 for i in range(n):
  j=max(range(i,n),key=lambda k:abs(m[k][i]))
  if abs(m[j][i])<1e-9:return None
  m[i],m[j]=m[j],m[i];v=m[i][i]
  for q in range(i,n+1):m[i][q]/=v
  for k in range(n):
   if k==i:continue
   v=m[k][i]
   for q in range(i,n+1):m[k][q]-=v*m[i][q]
 return [m[i][n] for i in range(n)]
def features(r,keys):return [1]+[math.log(r["n"]) if k=="logn" else r[k] for k in keys]
def fit(d,keys):
 X=[features(r,keys) for r in d];p=len(X[0])
 A=[[sum(x[i]*x[j] for x in X) for j in range(p)] for i in range(p)]
 b=[sum(x[i]*r["price"] for x,r in zip(X,d)) for i in range(p)]
 return solve(A,b)
def metrics(d,keys):
 beta=fit(d,keys)
 if beta is None:return None
 pred=[sum(v*w for v,w in zip(features(r,keys),beta)) for r in d]
 avg=statistics.mean(r["price"] for r in d)
 sse=sum((r["price"]-p)**2 for r,p in zip(d,pred))
 sst=sum((r["price"]-avg)**2 for r in d)
 p=len(beta)
 errs=[]
 for i,r in enumerate(d):
  b=fit(d[:i]+d[i+1:],keys)
  if b is None:return None
  errs.append((r["price"]-sum(v*w for v,w in zip(features(r,keys),b)))**2)
 return (1-sse/sst,1-(sse/(len(d)-p))/(sst/(len(d)-1)),math.sqrt(statistics.mean(errs)))
lines=["# 既存データの統合頑健性検証（再現可能）","","データ：1996・2026年に共通する10km圏地価地点5以上の地域と、30年以上のERA5系列。追加の外部API取得なし。","",
"## 地理的近接性を考慮した感度分析","","| 条件 | 地域数 | 気温–地価 Pearson r | 積雪–地価 Pearson r |","|---|---:|---:|---:|"]
for km in [0,10,20,30]:
 groups=clusters(km) if km else [[r] for r in data]
 reps=[max(g,key=lambda r:r["n"]) for g in groups]
 lines.append(f"| {km}km近接連結グループ（0kmは未統合） | {len(reps)} | {corr(reps,'temp'):+.3f} | {corr(reps,'snow'):+.3f} |")
lines+=["","**注意：** 近接連結は地価地点の共有を直接判定するものではない。連結鎖によってグループ端点が閾値以上離れる場合がある。","","## 回帰と1地域除外交差検証","","| モデル | n | R² | 調整済R² | LOOCV RMSE（地価変化率のポイント） |","|---|---:|---:|---:|---:|"]
for name,keys in [("平均のみ",[]),("気候",["temp","snow"]),("緯度・経度・log地点数",["lat","lon","logn"]),("地理代理＋気候",["lat","lon","logn","temp","snow"])]:
 m=metrics(data,keys)
 if m:lines.append(f"| {name} | {len(data)} | {m[0]:.3f} | {m[1]:.3f} | {m[2]:.2f} |")
lines+=["","## 重要な限界","",
"- 緯度・経度・地価地点数は人口、観光需要、都市近接性そのものではない。人口等を統制した因果推定ではない。",
"- 隣接地域は地価地点が重複する可能性があり、LOOCVも独立性を保証しない。",
"- 地価は名目価格・残存調査地点の中央値であり、取引価格や実質価格ではない。",
"- 30年気候系列と40年系列の傾きは観測期間が異なるため直接比較に注意。",
"- R²が高い地理代理モデルは因果説明ではなく、過学習・サンプル選択の可能性がある。",
"- いずれの分析も温暖化の地価への因果効果を識別しない。","","## 研究目的に対する判断","現有データからは気候指標が30年間の地価変化を安定して説明するという証拠は得られていない。ただし気候影響が存在しないことの証明でもない。",""]
out=P/"reports/integrated_climate_land_robustness_ja.md"
out.write_text("\n".join(lines),encoding="utf-8")
print("Wrote",out,"n",len(data))
