# Distance-quality audit: preliminary 2026 resort-to-land-price join

The exploratory join has 31 matched ski-area names and 141 nearest-point rows. **Only 29 of 31 resorts have a nearest-point row** in the current 0.25° latitude / 0.35° longitude candidate window.

| Distance to closest official land-price point | Resorts |
|---|---:|
| 0–2 km | 11 |
| >2–5 km | 2 |
| >5–10 km | 5 |
| >10–20 km | 6 |
| >20 km | 5 |
| **With at least one match** | **29** |
| **Without match** | **2** |

Only **13 of 31** matched resorts have an official land-price point within 5 km. Eleven have their nearest recorded point over 10 km away. This is a serious spatial-coverage constraint and makes a pooled 'nearby land prices' average misleading.

Examples of distant first matches: 音威富士スキー場 26.523 km, ほろたちスキー場 25.670 km, 国設南ふらのスキー場 24.028 km, 中頓別町寿スキー場 15.513 km.

## Interpretation
These are straight-line distances from OSM feature centers, **not road travel times**, and OSM centers are not verified entrances. Proximity alone does not establish that the land point belongs to the resort's economic catchment. A 5-km threshold would retain 13 facilities, but this cutoff must be tested for sensitivity (e.g. 2, 5, 10 km). No causal climate or land-price claim is warranted.

Source: `data/resort_landprice_nearest_2026.csv`.
