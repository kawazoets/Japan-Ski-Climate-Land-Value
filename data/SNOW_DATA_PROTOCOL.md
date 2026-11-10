# Snow and ski-season measurement protocol

## Source
The Japan Meteorological Agency (JMA) publishes historical daily **maximum snow depth** (日最深積雪) at stations where snow is observed: https://www.data.jma.go.jp/risk/obsdl/ . Download by selected station, item, and dates; preserve quality/homogeneity metadata and the original source file. JMA warns against excessive automated access. This project does **not** scrape JMA endpoints.

## Import format
Normalize downloaded observations into `data/jma_daily_snow_depth.csv` with columns:

```csv
station_id,date,snow_depth_cm,quality_code
```

One row per station and day. Date is YYYY-MM-DD. Leave missing depth blank, **never zero-fill missing values**. Keep JMA quality codes (do not silently discard flagged values). A separate station metadata file should record JMA station name, latitude/longitude, altitude, station type, and observation/homogeneity changes.

Optional mapping: `data/resort_jma_station_mapping.csv` with columns `resort_name,station_id,distance_km,verification_status`. Only rows explicitly marked `verified` are joined to resort names. A nearest station is not automatically representative of ski-slope conditions.

## Indicators
For each Nov 1–Apr 30 season (named by its April year): observed days, completeness, days with snow depth >=10 cm and >=30 cm, maximum and median depth. Only seasons with >=90% daily coverage are marked usable. These thresholds are **weather proxies, not resort operating days**. The snow cover at a weather station cannot establish ski lifts' opening days. Operating-day series must be independently collected from official resort announcements or operator reports and checked for closures due to wind, finance, and other factors.

## Analysis design
Link ski-resort operating days to local snow metrics and municipal land-price panel by year, with year and municipality effects, tourism and population controls, altitude, access, and regional trends. Do not attribute price changes to warming without a credible comparison group and pre-trend checks.

Run locally: `python scripts/aggregate_jma_snow_seasons.py` once normalized JMA daily data exist. No GitHub Actions workflow or notification is created.
