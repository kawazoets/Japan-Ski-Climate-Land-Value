# Preliminary 2026 land-price proximity matching

- Resort-name matched OSM candidates: 31
- Official 2026 MLIT land-price point features: 25565
- Nearest-point candidate rows (up to five per resort): 141
- Source: https://nlftp.mlit.go.jp/ksj/gml/data/L01/L01-26//L01-26_GML.zip
- Output: `data/resort_landprice_nearest_2026.csv`

**Cautions:** OSM feature centers are not verified resort entrances; nearest land-price points may be in a different market or land-use category. L01_008 is 2026 land price (JPY/m²) subject to official schema confirmation. These are exploratory spatial joins, not evidence that climate change affects land prices. A historical panel and controls are required.
