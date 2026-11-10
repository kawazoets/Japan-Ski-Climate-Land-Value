# Reproducible collection protocol
1. `osm_ski_candidates.csv` is a candidate discovery table, **not** a count of Japanese ski resorts. OSM entries include pistes, ski stations, overlapping objects and potentially closed areas. Never report its row count as the number of operating resorts.
2. Match named areas to official resort websites, prefectural lists or a licensed resort registry. Preserve official URL, verification date, municipality, and status; keep unresolved candidates separate.
3. Do not fabricate resort-season operating days from first/last dates. Keep actual operating days null until supported by daily records or official season reports.
4. Use MLIT annual land-price point files and maintain stable point IDs, coordinate distance, land use and municipality. Compare same land-use type and stable observation points.
5. Analyze potential confounding from demographic decline, foreign tourism, rail/highway access, investments and snowmaking. Closures create survivor bias.
6. GitHub Actions: source availability audit weekly; OSM candidate discovery monthly. Workflows must be enabled and have write permissions; scheduling may be delayed by GitHub. These workflows do not yet acquire actual operating days or MLIT price series.
7. Source for annual land-price GIS (2026, 2025, 2024 etc.): https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-L01-2026.html
8. OSM data attribution: © OpenStreetMap contributors, ODbL. https://www.openstreetmap.org/copyright
