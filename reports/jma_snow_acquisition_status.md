# JMA snow-depth data acquisition: station shortlist and gaps

The official JMA snow-station master has been matched by coordinates to the 13 ski resorts in the preliminary land-price pilot.

- 13 first-ranked stations (not independently validated for slope representativeness).
- 8 first-ranked stations within 5 km.
- 10 within 10 km.
- 3 over 10 km (興部町営, 北見市留辺蘂町八方台, 上富良野町日の出).
- 0 stations with confirmed daily 2016–2026 snow-depth coverage in the repository.
- 0 actual daily snow-depth observations acquired.

## Initial pilot stations

| Resort | JMA station | ID | Distance |
|---|---|---|---:|
| 下川町スキー場 | 下川 | 12925 | 0.259 km |
| 美深スキー場 | 美深 | 12900 | 1.805 km |
| 新得山スキー場 | 新得 | 20930 | 1.930 km |
| マウントレースイスキー場 | 夕張 | 15925 | 2.064 km |
| 上川町営中山スキー場 | 上川 | 12920 | 2.205 km |
| 富良野スキー場 | 富良野 | 12940 | 4.904 km |

These are good **candidates for testing data completeness**, not confirmed climate proxies. A slope can be hundreds of meters above its station. Station continuity, observation start dates, quality flags, and the distinction between daily maximum snow depth and snowfall need verification.

## Next verifiable acquisition step

Acquire JMA daily maximum snow-depth (日最深積雪) records for the six candidate station IDs for Nov–Apr seasons 2016–2026 using the official [JMA historical data download interface](https://www.data.jma.go.jp/risk/obsdl/). Keep original CSVs and normalize to `data/jma_daily_snow_depth.csv` with `station_id,date,snow_depth_cm,quality_code`.

Only then run `scripts/aggregate_jma_snow_seasons.py`. Do **not** populate the series with simulated weather, zeros for missing days, or station-level estimates. A daily station series cannot establish actual ski-lift operating days.

No automated JMA data scraping, recurring Actions workflow, or email notification is configured by this stage.
