import csv,collections,statistics,math
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def read(p):
 with (P/p).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
land=read("data/ski_resort_observed_land_price_1996_2026.csv")
climate=read("data/ski_region_reanalysis_climate_1986_2025.csv")
regions={}
for r in land:
 if r["radius_km"]=="10" and r["year"]=="2026" and r["median_same_point_change_pct"] and int(r["matched_1996_2026_point_count"] or 0)>=5:
  regions[r["candidate_id"]]=r
series=collections.defaultdict(dict)
for r in climate:
 if r["mean_temperature_c"] and r["winter_snowfall_cm"]:series[r["candidate_id"]][int(r["year"])]=r
def slope(v):
 xs=[x for x,y in v];ys=[y for x,y in v];mx=statistics.mean(xs);my=statistics.mean(ys)
 den=sum((x-mx)**2 for x in xs)
 return sum((x-mx)*(y-my) for x,y in v)/den if den else float("nan")
def corr(x,y):
 if len(x)<3:return None
 mx=statistics.mean(x);my=statistics.mean(y)
 den=math.sqrt(sum((v-mx)**2 for v in x)*sum((v-my)**2 for v in y))
 return sum((a-mx)*(b-my) for a,b in zip(x,y))/den if den else None
# A sample-size threshold alone cannot establish validity or causality.
def validity_assessment(pairs):
 n=len(pairs)
 return (f"EXPLORATORY ONLY: {n} climate-land matched resort observations. "
         "No arbitrary minimum sample count is treated as proof of validity. "
         "Spatial overlap, demographic and tourism confounding, and incomplete "
         "climate coverage remain; causal warming effect NOT identified.")
pairs=[]
for cid,r in regions.items():
 vals=series.get(cid,{})
 if len(vals)<30:continue
 t=slope([(y,float(v["mean_temperature_c"])) for y,v in vals.items()])
 snow=slope([(y,float(v["winter_snowfall_cm"])) for y,v in vals.items()])
 pairs.append((r["resort_name"],float(r["median_same_point_change_pct"]),t*10,snow*10,int(r["matched_1996_2026_point_count"])))
alltemps=[]
for cid,vals in series.items():
 if len(vals)>=30:alltemps.append(slope([(y,float(v["mean_temperature_c"])) for y,v in vals.items()])*10)
changes=[p[1] for p in pairs];temps=[p[2] for p in pairs];snows=[p[3] for p in pairs]
fmt=lambda x:"not estimable" if x is None else f"{x:+.3f}"
lines=["# 日本のスキー場周辺地価と温暖化：最終検証（現有データ）","","## 結論","",
"**1996〜2026年の地価下落は広範囲に観測された。しかし現有データでは、温暖化がその下落を引き起こした、あるいは何割を説明するかは実証できない。**","",
"## 観測できた不動産価値の変化","",
"- 全国451候補中228候補に暫定位置情報。10km圏内に1996年・2026年共通の地価調査地点が5件以上ある44地域が比較可能。",
"- 44地域のうち42地域で名目地価下落、2地域で上昇。地域別変動率の中央値は -55.2%。",
"- 上昇地域は札幌藻岩山（+10.5%）、さっぽろばんけい（+8.1%）。都市近接性が影響した可能性はあるが、検証されていない。",
"",
"## 気象との統合検証","",
f"- ERA5気象系列を取得できたスキー場候補: {len(series)}地域（1986〜2025年）。",
f"- 30年以上の有効な気温系列がある地域: {len(alltemps)}。",
f"- 気温系列を持ち、かつ10km圏内で地価の長期比較が可能な地域: **{len(pairs)}**。",
f"- 気温の10年当たり変化率（気象系列がある地域の中央値）: {statistics.median(alltemps):+.3f} ℃/10年。" if alltemps else "- 気温の傾向は推計不能。",
f"- 地価変化率と気温トレンドのPearson相関: {fmt(corr(changes,temps))} (n={len(pairs)})。",
f"- 地価変化率と冬季積雪トレンドのPearson相関: {fmt(corr(changes,snows))} (n={len(pairs)})。",
"",
"### 結合できた地域（10km圏）","","| 地域 | 1996–2026地価変化 | 気温変化 ℃/10年 | 積雪変化 cm/10年 | 共通地価地点数 |","|---|---:|---:|---:|---:|"]
for name,price,t,snow,n in sorted(pairs,key=lambda x:x[1]):
 lines.append(f"| {name} | {price:+.1f}% | {t:+.3f} | {snow:+.1f} | {n} |")
lines+=["","## 妥当性判定","",validity_assessment(pairs),"","## 解釈上の制約","",
"- 気象はERA5再解析の格子推計値であり、山岳斜面の現地観測ではない。1986〜2025年の一部地域のみで、2026年気象は含まれない。",
"- 冬季積雪は同一暦年の1〜4月・11〜12月を合算しており、スキーシーズン単位ではない。",
"- 地価は2026年に存続する標準地の名目価格であり、調査地点の生存バイアスがある。リゾート物件の取引価格ではない。",
"- 隣接スキー場の10km圏は重複するため、地域ごとの結果は独立とは限らない。",
"- 人口減少、都市近接性、観光需要、土地利用、インフレ、資本流入を統制していない。",
"- 気候と地価の相関が計算可能でも因果効果ではない。サンプルが少ない場合、相関値の解釈は不適切。",
"",
"## 研究の到達点","",
"本研究の現有データで確立できたのは、30年間のスキー場周辺地価の地域差と、利用可能な気象系列の限定的な比較までである。**地球温暖化が不動産価値をどれほど変えたかという本来の因果的問いには、現状では答えられない。** 欠測期間の偏り、地価地点の共有、人口・観光需要等の交絡を検証し、研究目的に対する結論を再評価する必要がある。"]
(P/"reports/final_ski_climate_land_value_research_ja.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("final report",len(pairs),"matched; climate",len(series))
