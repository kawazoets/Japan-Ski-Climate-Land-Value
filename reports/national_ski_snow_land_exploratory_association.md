# Exploratory nationwide ski-area snow trend and nearby land price change

**This is descriptive and not evidence that shortened ski seasons cause land-price declines.**

Eligibility: resort linked to JMA station within 20 km, all 10 winters usable (Nov–Apr, 2016–2025 winter starts), and at least 5 matched MLIT price points in each tested land-price radius.

| Land radius | Eligible resorts | Pearson r: snow >=1cm days trend vs land price | Pearson r: snow >=30cm days trend vs land price |
|---|---:|---:|---:|
| 10 km | 39 | -0.125 | -0.374 |
| 20 km | 107 | 0.009 | -0.172 |

## Essential limitations

- Ten winters are a short climate window; linear slopes are descriptive and noisy.
- JMA station snow days are **not** actual resort operating days. Operating-day series are not yet available.
- Ski resort coordinates are provisional and JMA station elevation may differ materially from ski slope elevation.
- The MLIT 2016–2026 matched-point cohort includes only 2026-surviving price points (survivorship bias).
- No adjustment for tourism demand, infrastructure, transport, urbanization, property type, elevation or resort closures.
- Multiple resorts may share the same JMA station and land-price points; rows are not statistically independent.
- Correlation here cannot establish temporal or causal effects; do not use p-values treating resort rows as independent.
