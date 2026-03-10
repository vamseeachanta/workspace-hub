---
name: production-forecaster
description: Forecast oil & gas well production using decline curve analysis. Use when estimating EUR, generating type curves, fitting Arps models (exponential, hyperbolic, harmonic), or running reserve calculations. Supports conventional and unconventional wells, P10/P50/P90 probabilistic outputs, and multi-field type curve comparison.
version: 2.1.0
category: data/energy
last_updated: 2026-03-08
capabilities: []
requires: []
see_also:
  - ../npv-analyzer/SKILL.md
  - ../bsee-data-extractor/SKILL.md
  - ../field-analyzer/SKILL.md
---

# Production Forecaster

Forecast oil and gas production using industry-standard decline curve analysis.
Supports Arps decline models, type curve generation, and EUR calculations for
reserve estimation.

## When to Use

- Forecasting future production for oil and gas wells
- Estimating EUR (Estimated Ultimate Recovery)
- Generating type curves for field development planning
- Fitting decline parameters to historical production data
- Comparing well performance across different fields
- Supporting reserve booking and economic evaluation

## Core Pattern

```
Historical Production → Decline Curve Fit → Parameter Estimation → Forecast → EUR
```

## Decline Curve Models

### Arps Equations

| Model | Equation | b value | Typical Use |
|-------|----------|---------|-------------|
| Exponential | `q(t) = qi * exp(-Di * t)` | 0 | Mature conventional |
| Hyperbolic | `q(t) = qi / (1 + b*Di*t)^(1/b)` | 0–1 | Most common |
| Harmonic | `q(t) = qi / (1 + Di*t)` | 1 | Fracture-dominated |
| Modified Hyperbolic | Hyperbolic until D(t) ≤ D_min, then exponential | — | Long-term forecast |

Parameters: `qi` = initial rate, `Di` = initial decline rate, `b` = exponent, `t` = time.

### Unconventional Models

**Duong** (transient linear flow): `q(t) = q1 * t^(-m) * exp(-a/(1-m) * (t^(1-m) - 1))`

**Stretched Exponential**: `q(t) = qi * exp(-(t/τ)^n)`

See `references/examples.md` for full class implementations and fitting code.

## Key Classes

| Class | Purpose |
|-------|---------|
| `DeclineCurveAnalyzer` | Fit decline models to production data; calculate EUR and validation metrics |
| `ProductionForecaster` | Generate rate/cumulative forecasts from fitted parameters |
| `TypeCurveGenerator` | Normalize wells, bin by attribute, generate P10/P50/P90 type curves |
| `ProductionReportGenerator` | Render interactive HTML reports via Plotly |

### Quick Start — Single Well

```python
from production_forecaster import DeclineCurveAnalyzer, ProductionForecaster
import pandas as pd

historical = pd.read_csv('data/production/well_a1.csv')  # columns: date, rate

analyzer = DeclineCurveAnalyzer(historical)
params, model_type = analyzer.fit_best_model()           # picks best RMSE fit

forecaster = ProductionForecaster(params, cumulative_to_date=historical['cumulative'].iloc[-1])
forecast = forecaster.forecast(years=30, economic_limit=25)

print(f"Model: {model_type} | EUR: {forecast.eur_oil/1e6:.2f} MMbbl")
```

### Quick Start — Type Curves

```python
from production_forecaster import TypeCurveGenerator, NormalizationMethod, TypeCurveBinType
import pandas as pd, glob

wells = [pd.read_csv(f) for f in glob.glob('data/production/field_x/*.csv')]
generator = TypeCurveGenerator(wells, metadata=well_metadata)
generator.normalize_wells(method=NormalizationMethod.IP_30)
generator.create_bins(TypeCurveBinType.WATER_DEPTH)

bin_results = generator.generate_bin_type_curves(TypeCurveBinType.WATER_DEPTH)
eur_dist = generator.calculate_eur_distribution(economic_limit=25)
```

## Type Curve Normalization Methods

| Method | Key | Best For |
|--------|-----|----------|
| Peak rate | `peak` | Clear IP wells |
| First month avg | `first_month` | Consistent start-up |
| 30-day IP | `30_day_ip` | Standard industry definition |
| 90-day IP | `90_day_ip` | More stable baseline |
| Moving average | `moving_average` | Noisy data |

Bins: `formation`, `completion`, `water_depth`, `lateral_length`, `proppant`, `vintage`.
Percentiles: P10 = optimistic (90th), P50 = median, P90 = conservative (10th).

## CLI Summary

```bash
# Fit and forecast
uv run --no-project python -m production_forecaster fit --data well.csv --model hyperbolic
uv run --no-project python -m production_forecaster forecast --config config/forecast.yaml

# Type curves
uv run --no-project python -m production_forecaster type-curve \
    --wells data/production/*.csv --normalize 30_day_ip --bin-by water_depth

# EUR
uv run --no-project python -m production_forecaster eur --qi 5000 --di 0.35 --b 0.8 --limit 25
```

Full CLI options, YAML config templates, and complete class implementations:
→ `references/examples.md`

## Best Practices

**Data quality**: Clean outliers; use ≥6–12 months of decline data; account for
workovers and shut-ins.

**Model selection**: Exponential for mature conventional; hyperbolic for most
unconventional; high b (>1) for extended linear flow. Use modified hyperbolic
for long-term forecasts to cap optimism with a terminal decline rate (5–8%/year).

**Uncertainty**: Always generate P10/P50/P90. Update forecasts quarterly.
Document all assumptions for reserve booking.

## Data Models (summary)

```
DeclineParameters(qi, di, b, decline_type, min_rate, d_min, a, m, tau, n)
ProductionRecord(date, oil_rate, gas_rate, water_rate, days_on)
ForecastResult(dates, oil_rates, gas_rates, cumulative_oil, eur_oil, remaining_oil, ...)
TypeCurveResult(months, p10/p50/p90_rates, mean_rates, well_counts, eur_p10/p50/p90, ...)
```

Full dataclass definitions in `references/examples.md §Data Models`.

## Related Skills

- `../npv-analyzer/SKILL.md` — Economic evaluation with Monte Carlo simulation
- `../bsee-data-extractor/SKILL.md` — Extract BSEE production, WAR, and APD data
- `../field-analyzer/SKILL.md` — Field-level production analysis
- `../well-production-dashboard/SKILL.md` — Production visualization

---
*v2.0.0 (2025-12-30): Initial release. v2.1.0 (2026-03-08): Trimmed to thin guide; bulk content → references/examples.md.*
