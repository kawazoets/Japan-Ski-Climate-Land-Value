# Sensitivity of nationwide snow trend versus land-price correlations

**Descriptive associations only. Snow station coverage is not ski-resort operating duration.**

| Radius | Sample definition | N | Pearson r (30cm snow days) | Spearman rho | Leave-one-resort-out Pearson range |
|---|---|---:|---:|---:|---|
| 10 km | All eligible resorts | 39 | -0.374 | -0.458 | -0.399 to -0.314 |
| 10 km | Exclude >=50% land appreciation | 35 | -0.354 | -0.345 | -0.412 to -0.270 |
| 10 km | Exclude >=30% land appreciation | 34 | -0.270 | -0.298 | -0.346 to -0.179 |
| 10 km | At least 20 matched land points | 11 | -0.341 | -0.517 | -0.544 to -0.206 |
| 10 km | One resort per JMA station (max land points) | 18 | -0.267 | -0.253 | -0.379 to -0.128 |
| 20 km | All eligible resorts | 107 | -0.172 | -0.183 | -0.193 to -0.144 |
| 20 km | Exclude >=50% land appreciation | 98 | -0.097 | -0.121 | -0.117 to -0.072 |
| 20 km | Exclude >=30% land appreciation | 97 | -0.108 | -0.116 | -0.131 to -0.081 |
| 20 km | At least 20 matched land points | 48 | -0.359 | -0.480 | -0.391 to -0.317 |
| 20 km | One resort per JMA station (max land points) | 51 | -0.144 | -0.228 | -0.188 to -0.083 |

## Interpretation rules

- A sign change under simple exclusions indicates instability, not a reliable association.
- Resort observations sharing JMA stations or overlapping MLIT buffers are not independent.
- 2016–2026 land changes are a single endpoint difference, while snow trends are based on ten winters.
- Urban proximity, property type, ski-area elevation, and resort operation status are uncontrolled.
- Land-point survival to 2026 creates selection bias; no inference about closed resorts or missing points.
- Spearman rank correlation reduces sensitivity to extreme percentage changes but cannot correct confounding.
