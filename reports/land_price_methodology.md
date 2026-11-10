# Official land-price source and analysis design

## Primary data
MLIT National Land Numerical Information, land-price publication (地価公示), L01, reference date January 1 each year. Official data page: https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-L01-2026.html

The official page lists **national** GML ZIP archives from 2007 through 2026, including 2026 `L01-26_GML.zip` (~19.9 MB). For 2019 onward the license is CC BY 4.0; check original terms for earlier years. Official records contain coordinates, land-price and land-use attributes. No API key is needed to use the downloadable GIS archives. Data files have **not** yet been downloaded into this repository.

## Alternative measure
MLIT prefectural land-price survey (都道府県地価調査), reference date July 1, includes potentially different observation points. Do not splice this with January 1 L01 records as though it were the same time series.

## Unit of analysis
For each year, retain stable survey point ID, municipality code, latitude, longitude, land-use category, nominal JPY/m² and observation date. Identify genuinely matched points across years; survey point identifiers or coordinates may change, so name/ID matches must be audited.

For ski resort exposure, use verified resort coordinates and road accessibility (not just Euclidean distance). Distinguish resort vicinity from residential or commercial property in the gateway town. Avoid treating land-price points absent from mountain terrain as a zero-price observation.

## Causal identification
Compare exposed municipalities with otherwise similar snow-region municipalities and include municipality and year fixed effects, demographic and tourism controls, and resort closures. Weather anomalies are not equivalent to long-term climate change; test a longer time series and compare pre-trends.

## Data integrity gates
- Do not infer the number of operating resorts from an unverified web directory.
- Do not treat first-to-last operating date span as actual operating days.
- Do not assert any climate–land-price correlation until resort coordinates, verified season records and official land-price points are joined.
- Preserve closed facilities to mitigate survivorship bias.

## Verified official references
- https://www.mlit.go.jp/report/press/tochi_fudousan_kensetsugyo17_hh_000001_00078.html
- https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-L01-2026.html
- https://www.mlit.go.jp/report/press/tochi_fudousan_kensetsugyo17_hh_000001_00089.html
