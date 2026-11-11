# Nationwide ski-resort × MLIT 2016–2026 land-price linkage

- Candidate resorts retained (including closed/paused): **451**
- Candidate resorts with one provisional OSM geometry: **228**
- Official MLIT 2026 point IDs in input: **25565**
- Identical point IDs with both 2016 and 2026 prices: **22402**
- Resort–point pairs within 20 km: **7136**
- Resort/radius rows (including explicit no-data cases): **1804**

This is a descriptive geographic buffer analysis, not a causal estimate. Each
ski resort location is an unverified OSM geometry. Nearby resorts can share
the same land-price point, so observations are not independent. Only land-price
points retained in the 2026 dataset are represented; historical point closures
and changes of sampling frame create survivor bias. A 2026 coordinate is used
for all years, so relocations or land-use changes are not corrected. The
geographic buffer does not identify ski-related parcels or tourism exposure.
Missing geocodes and empty buffers remain explicit missing cases.
