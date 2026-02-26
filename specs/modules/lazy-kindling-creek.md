# WRK-318 — Arps Decline Curve Production Forecasting Module

## Context

worldenergydata already ingests BSEE monthly production data but has no forecasting capability.
WRK-318 adds Arps decline curve analysis (exponential / hyperbolic / harmonic) so users can fit
historical production, compute EUR, and generate forecast curves — all from the existing toolset.
BSEE binary data (~300 MB) is not in git; tests use synthetic data with known parameters.

---

## Module Location

```
src/worldenergydata/production/forecast/
├── __init__.py          → exports ArpsDeclineCurve, ForecastResult, ArpsModel
├── decline.py           → core class + result dataclass  (~250 lines)
└── cli.py               → typer app (top-level `forecast` subcommand)  (~80 lines)

src/worldenergydata/cli/commands/
└── production_forecast.py   → 3-line wrapper (mirrors cli/commands/metocean.py pattern)

src/worldenergydata/cli/main.py  → add_typer(forecast.app, name="forecast")

tests/unit/production/forecast/
├── __init__.py
└── test_decline.py      → ~12 unit tests, all synthetic data  (~130 lines)
```

---

## Data Structures

**`ForecastResult`** dataclass (`decline.py`):
```
model: str              # 'exponential' | 'hyperbolic' | 'harmonic'
qi: float               # fitted initial rate (bbl/month)
Di: float               # fitted nominal decline rate (1/month)
b: float                # hyperbolic exponent (0=exp, 1=harmonic)
r_squared: float        # goodness-of-fit
eur_bbl: float          # estimated ultimate recovery at economic limit
forecast_df: DataFrame  # columns: month, rate_bbl, cumulative_bbl
lower_ci: DataFrame|None
upper_ci: DataFrame|None
```

Input `production` DataFrame must have columns: `month` (int, 1-based) and `rate_bbl` (float).

---

## Arps Math

| Model | Rate equation | EUR |
|---|---|---|
| Exponential (b=0) | `qi·exp(−Di·t)` | `qi/Di · (1 − exp(−Di·t_econ))` |
| Hyperbolic (0<b<2) | `qi·(1 + b·Di·t)^(−1/b)` | `qi^b/((1−b)·Di) · (qi^(1−b) − q_econ^(1−b))` |
| Harmonic (b=1) | `qi/(1 + Di·t)` | `qi/Di · ln(qi/q_econ)` |

Fitting: `scipy.optimize.curve_fit` (nonlinear least squares).  Bounds: qi > 0, Di > 0, 0 < b < 2.

---

## ArpsDeclineCurve Class API (`decline.py`)

```python
class ArpsDeclineCurve:
    def fit(self, production: pd.DataFrame,
            model: str = "hyperbolic",
            economic_limit: float = 10.0) -> ForecastResult

    def forecast(self, result: ForecastResult, months: int = 120) -> pd.DataFrame

    def plot(self, historical: pd.DataFrame, result: ForecastResult) -> go.Figure

    # private helpers
    def _rate_fn(self, model) -> Callable
    def _compute_eur(self, qi, Di, b, economic_limit, model) -> float
    def _r_squared(self, actual, predicted) -> float
```

`fit()` validates input (`ValueError` on empty DF or unknown model), calls `curve_fit`, returns
`ForecastResult` with forecast_df pre-populated for `months=120`.

---

## CLI

```
worldenergydata forecast [--model hyperbolic|exponential|harmonic]
                         [--months 120]
                         [--econ-limit 10.0]
                         [--input path/to/production.csv]
                         [--output path/to/report.html]
```

`--input` CSV must have `month,rate_bbl` columns. If omitted, CLI uses the BSEE unified adapter
sample fields (Atlantis/Thunder Horse) and prints a table + saves HTML chart.

---

## TDD Order (strict: tests before implementation)

1. Write `tests/unit/production/forecast/__init__.py`
2. Write `tests/unit/production/forecast/test_decline.py` — all tests fail (RED)
3. Write `src/worldenergydata/production/forecast/__init__.py`
4. Write `src/worldenergydata/production/forecast/decline.py` — make tests GREEN
5. Write `src/worldenergydata/production/forecast/cli.py`
6. Write `src/worldenergydata/cli/commands/production_forecast.py`
7. Edit `src/worldenergydata/cli/main.py` — add forecast typer
8. Edit `src/worldenergydata/production/__init__.py` — re-export new symbols

---

## Test Cases (`test_decline.py`)

Helper: `_make_synthetic(model, qi, Di, b, n=60, noise=0.02, seed=42)` — generates known Arps
curve + Gaussian noise; parameters are recoverable to ±5% by the fitter.

| Test | What it checks |
|---|---|
| `test_fit_hyperbolic_recovers_qi` | fitted qi within 5% of known |
| `test_fit_exponential_recovers_qi` | same for b=0 |
| `test_fit_harmonic_recovers_qi` | same for b=1 |
| `test_fit_returns_forecast_result` | isinstance ForecastResult |
| `test_r_squared_above_threshold` | r² > 0.90 on clean synthetic |
| `test_eur_positive_finite` | eur_bbl > 0, not nan/inf |
| `test_forecast_df_columns` | ['month','rate_bbl','cumulative_bbl'] present |
| `test_forecast_monotonic_decline` | rate_bbl monotonically non-increasing |
| `test_plot_returns_figure` | isinstance go.Figure |
| `test_invalid_model_raises` | ValueError on model="invalid" |
| `test_empty_input_raises` | ValueError on empty DataFrame |
| `test_forecast_length` | forecast_df has requested months rows |

---

## Key Files to Reference

- Pattern (class + dataclass): `src/worldenergydata/metocean/statistics/scatter_diagram.py`
- CLI wrapper pattern: `src/worldenergydata/cli/commands/metocean.py`
- CLI registration: `src/worldenergydata/cli/main.py` (lines ~79–118)
- Production `__init__`: `src/worldenergydata/production/__init__.py`
- Test pattern: `tests/unit/metocean/statistics/test_scatter_diagram.py`
- Existing production module: `src/worldenergydata/production/unified/query.py`

---

## Verification

```bash
cd /mnt/local-analysis/workspace-hub/worldenergydata

# Run only the new tests (RED → GREEN cycle)
python3 -m pytest tests/unit/production/forecast/ -v --noconftest

# Smoke test CLI
python3 -m worldenergydata forecast --help
python3 -m worldenergydata forecast --model hyperbolic --months 60

# Full suite — confirm no regressions
python3 -m pytest tests/ --noconftest -q
```
