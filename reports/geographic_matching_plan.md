# Geographic matching — required verified resort input

The official 2026 L01 archive was downloaded and 25,565 point records extracted in GitHub Actions. The CSV is currently an Actions artifact, not committed to the repository.

## Missing prerequisite
A verified resort coordinate file at `data/resort_coordinates_verified.csv` with fields `resort_name,latitude,longitude,source_url` is needed. The 422 unverified directory entries must **not** be assigned guessed coordinates.

## Join method
`scripts/join_resorts_mlit.py` finds up to five nearest MLIT point candidates per verified resort, using great-circle distance. It does **not** claim these are the same real-estate market or that proximity establishes causation. Review municipality, land-use and transport accessibility before analysis.

## Important note
`L01_008` is retained as the raw official field in the provisional output. The field interpretation and unit must be checked against the official data dictionary before any published land-price comparison.

No background GitHub Actions or notification-triggering workflow has been added.
