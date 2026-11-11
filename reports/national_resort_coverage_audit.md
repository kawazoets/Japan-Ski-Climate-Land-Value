# Nationwide candidate coverage audit

- Directory candidate records retained: **451**
- Records in duplicate normalized-name groups: **0**
- Unique-name candidates with an exact-name OSM coordinate candidate: **0**
- OSM raw candidate records available: **0**
- Prior pilot resort names found in nationwide directory: **13**
- Remaining candidate records without unambiguous exact-name coordinates: **451**

**No candidates were discarded for missing coordinates, land-price points, station matches, or unknown closure status.**

The directory is an unverified third-party list and is not the Japan Ropeway Association's count of 417 operating ski areas. Counts are not interchangeable. Exact-name matches are **candidate coordinates, not verified facility locations**; duplicated names are withheld from automatic geocoding. The 13-resort pilot is a subset, not the national sampling frame.

## Next stages
1. Obtain/validate nationwide geocodes with source attribution and confidence; avoid conflating lift stations and resort polygons.
2. Verify operating/closed status, including historically closed areas, with date-specific evidence.
3. Assign municipality by administrative boundary polygons (not nearest land-price point).
4. Connect JMA station records and resort operating seasons, preserving coverage and missingness.
5. Compare matched-point land-price trends with controls and sensitivity checks.

Sources: `data/directory_candidates.csv` and optional `data/osm_ski_candidates.csv`.
