# Nationwide coordinate seeding audit

- Nationwide directory candidates retained: **458**
- Exact-name coordinate seeds recovered from existing OSM land-price join: **29**
- Ambiguous matches: **0**
- Remaining without coordinate seed: **429**
- Original 13-facility pilot flags retained: **13**

Coordinate seeds are **provisional**: a name match does not establish the correct ski-area location. No facility was excluded for missing coordinates or operating status. Data were computed directly from existing repository CSVs, without a GitHub Actions workflow or new external API requests. Japanese long-vowel mark ー was preserved during normalization.

Input: `data/national_ski_resort_candidate_master.csv`, `data/resort_landprice_nearest_2026.csv`.
