# Actual ski-resort operating days: source-backed evidence and research reset

## Research question
Do shorter **actual operating seasons** of Japanese ski resorts correlate with declines in nearby land prices between 2016 and 2026? Snow depth is a possible explanatory factor, **not** the operating-day outcome.

## Verified municipal operating-day series
The municipality of Memuro, Hokkaido, reports **actual operating days** for a municipal ski facility in its designated-manager performance report:

| Winter start | Actual days | First open | Last open |
|---|---:|---|---|
| 2015 | 87 | 2015-12-26 | 2016-03-21 |
| 2016 | 93 | 2016-12-18 | 2017-03-20 |
| 2017 | 93 | 2017-12-15 | 2018-03-21 |
| 2018 | 83 | 2018-12-20 | 2019-03-12 |
| 2019 | 80 | 2019-12-25 | 2020-03-15 |
| 2020 | 85 | 2020-12-25 | 2021-03-21 |

Official source: https://www.memuro.net/administration/soshiki/keiei/kanrisya/files/R2jhkokuminn.pdf

Machine-readable: data/municipal_ski_actual_operating_days_verified.csv. Facility identity has **not** yet been mapped to the 451-resort cohort. Do not merge until verified.

## Other official operating-day evidence
- Niigata prefecture, 2025-26 season: **4,146 total ski-resort operating days**, **94.1%** of prior season; prefecture explicitly attributes delayed opening and early closing to low snow and high temperatures. This is a **prefecture aggregate** and not a per-resort time series. https://www.pref.niigata.lg.jp/sec/kankokikaku/r7-8ski.html
- Nagano prefecture's 2023 ski-area policy report shows **average operating days** for 2015-16 to 2021-22 winters: **101.9, 107.9, 109.5, 107.3, 102.7, 107.9, 106.7** days. This is a **prefecture aggregate**, not evidence for an individual resort. https://www.pref.nagano.lg.jp/kankoshin/documents/20_sukizyouhoushin_hontai.pdf
- Nagano prefecture's survey of 37 facilities reports average **winter operating days** for FY2018 to FY2022: **96, 96, 109, 112, 107**. This is a **different sample** and must not be spliced into the above series. https://www.pref.nagano.lg.jp/kankoshin/documents/30_zittaityousakekka.pdf

## Evidence priority and stopping rules
1. Extract **per-resort actual operating days**, preferably municipal designated-manager annual reports, official resort annual reports, and prefectural per-facility spreadsheets.
2. Distinguish actual days from announced planned dates and calendar span; do not impute the former from the latter.
3. Verify resort identity against national candidate IDs before joining to snow and MLIT land-price data.
4. Only estimate a relationship with land prices for resorts with **at least two independently sourced winter seasons**, and label short series as exploratory.
5. Keep prefecture aggregates separate and report the fraction of the 451 resorts with actual operating-day coverage.
6. Do **not** spend more effort on snow-land correlations that omit actual operating days.
