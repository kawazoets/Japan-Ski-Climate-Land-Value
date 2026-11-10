# Exploratory 2016–2026 residential land-price change near matched ski areas

This is an **illustrative subset**, not a national estimate. The 13 ski-area OSM centers with a nearest MLIT land-price survey point within 5 km were assigned the **municipality code of that nearest survey point**, which is a proxy and not a verified resort municipality. The municipality's matched 2016/2026 points classified as **住宅** in the 2026 dataset were then compared.

| Ski area | Nearest survey point (km) | Proxy municipality code | Matched residential points | Median of point-level changes, 2016–2026 |
|---|---:|---|---:|---:|
| 伊ノ沢市民スキー場 | 1.055 | 01204 | 56 | 0.000% |
| 富良野スキー場 | 2.514 | 01229 | 3 | 0.000% |
| 新得山スキー場 | 1.172 | 01635 | 2 | -5.227% |
| マウントレースイスキー場 | 1.379 | 01209 | 2 | -35.516% |
| 美幌町リリー山スキー場 | 1.756 | 01543 | 2 | -11.930% |
| 枝幸町三笠山スキー場 | 1.257 | 01514 | 2 | -18.772% |
| 美深スキー場 | 0.822 | 01469 | 2 | -23.385% |
| 興部町営スキー場 | 1.622 | 01561 | 2 | -21.355% |
| 北見市留辺蘂町八方台スキー場 | 1.800 | 01208 | 11 | 0.000% |
| かもい岳国際スキー場 | 2.198 | 01227 | 2 | -31.761% |
| 上富良野町日の出スキー場 | 0.692 | 01460 | 2 | -16.525% |
| 下川町スキー場 | 0.520 | 01468 | 2 | -9.395% |
| 上川町営中山スキー場 | 0.811 | 01457 | 2 | -31.677% |

**Quality:** Only two of these thirteen municipality/land-use groups have five or more matched residential survey points. Most have two, making municipality medians unstable. The 2026 archive only contains the historical series for points retained in 2026 (survivorship bias). Figures are nominal and not inflation adjusted. Municipality assignment is inferred from nearest point, not administrative polygon containment. The ski areas have no linked season-length or snowfall observations, so **none of these price movements can yet be attributed to warming or shortened ski seasons**.

Sources: `data/resort_landprice_nearest_2026.csv`, `data/mlit_municipality_matched_2016_2026.csv`. Matching criterion: nearest_rank=1 and distance_km<=5; residential use equals 住宅.
