# Matched survey-point price change, 2016–2026

- Source: https://nlftp.mlit.go.jp/ksj/gml/data/L01/L01-26//L01-26_GML.zip
- 2026 source survey points: 25565
- Points with positive prices in **both 2016 and 2026**: 22402
- Municipality × current land-use groups with matched points: 5289
- Groups with at least five matched points: 980
- Output: `data/mlit_municipality_matched_2016_2026.csv`

`median_point_change_pct` is the median of individual matched-point percentage changes, whereas `median_of_price_ratios_pct` is the percentage change in the two cross-sectional medians for those same points. They need not agree.

**Limitations:** This conditions on a point appearing in the 2026 file, so earlier-closed points are omitted. Current land-use is used for grouping, not necessarily historical land-use. Nominal prices are not inflation-adjusted. A municipality with few matched points cannot support a stable local trend. No ski-resort exposure, weather data or causal identification is included yet.
