# Japan Ski Climate Land Value

Research question: Does shortening ski resort operating season correlate with changes in nearby land prices in Japan?

## Status (2026-11-10)
- Baseline: 417 operating ski resorts in 2025 (Japan Ropeway Association count, reported by Kyodo). The resort-level roster is **not yet verified**.
- No resort-level observations or land-price matches have been collected yet. Do not treat the 417 count as a dataset.
- Next: obtain the authoritative facility roster, reconcile names and coordinates, and preserve sources and missingness.

## Data definitions
- `data/resorts.csv`: one row per verified resort, source and coordinate provenance mandatory.
- `data/seasons.csv`: resort-season observations; scheduled open/close versus actual operating days are different measures.
- `data/land_prices.csv`: MLIT published land-price points, with location and reference year.

## Method
1. Build a verifiable roster, including closed and renamed resorts for historical comparison.
2. Collect operating dates and actual closure days where available; keep missing data blank.
3. Match land-price observations geographically, distinguishing resort land, commercial districts and residential districts.
4. Compare changes with controls for population, tourism demand, access, resort altitude and general land-price trends. Correlation does not prove climate causation.

## Sources
- Kyodo report on 417 resorts: https://news.jp/i/1380113804442730560
- MLIT 2026 land prices: https://www.mlit.go.jp/report/press/tochi_fudousan_kensetsugyo17_hh_000001_00078.html
- MLIT 2026 prefectural land survey: https://www.mlit.go.jp/report/press/tochi_fudousan_kensetsugyo17_hh_000001_00089.html
- MLIT API documentation: https://www.reinfolib.mlit.go.jp/help/apiManual/

No automated scraping of websites without verifying terms, permissions, and data quality.

## Verified scope notes (2026-11-10)
- The 417 count is **not** a publicly verified roster of 417 named facilities. Kyodo's January 2026 reporting attributes it to the Japan Ropeway Association's count of operating lift-served ski areas in 2025. Prefecture counts: Hokkaido 92, Nagano 80, Niigata 46. Source: https://news.jp/i/1380113804442730560
- MLIT's XPT002 land-price point API covers published land-price points since 1995 and prefectural land-price survey points since 1997: https://www.reinfolib.mlit.go.jp/help/apiManual/xpt002/
- MLIT's XIT001 transaction-price API covers transactions from 2005 Q3 onward: https://www.reinfolib.mlit.go.jp/help/apiManual/xit001/
- MLIT says API usage requires an application: https://www.mlit.go.jp/tochi_fudousan_kensetsugyo/tochi_fudousan_kensetsugyo_tk17_000001_00038.html
- Prefer downloadable GIS/CSV land-price data if API credentials are not available. Do not commit any API key to a public repository.

## Research caution
Resort count is affected by closures, mergers, renamed facilities and changes in lift operations. Avoid survivor bias: include historic closures in a separate cohort, rather than examining only today's operating resorts. Nearby land-price points may be sparse or in different land-use categories; record distances and land-use explicitly.
