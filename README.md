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
