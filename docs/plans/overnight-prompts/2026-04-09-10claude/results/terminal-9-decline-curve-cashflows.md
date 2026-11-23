# Terminal 9 — Production Decline Curve to Economics Cashflow Model

## Issue Metadata

| Field          | Value                                                                              |
| -------------- | ---------------------------------------------------------------------------------- |
| Issue          | #2054                                                                              |
| Title          | feat(field-dev): add production decline curve to economics cashflow model          |
| Labels         | enhancement, cat:engineering, domain:code-promotion, agent:claude                  |
| Parent epic    | #1858 (economics facade)                                                           |
| Related        | #1845 (production profiles)                                                        |
| Status         | NOT IMPLEMENTED — dossier only                                                     |
| Dossier date   | 2026-04-09                                                                         |

---

## 1. Current-State Findings

### 1.1 Files / Modules Already Present

#### Primary target — `digitalmodel`

| File | Lines | Relevance |
|------|-------|-----------|
| `digitalmodel/src/digitalmodel/field_development/economics.py` | 693 | Contains `EconomicsInput` (L75-132), `_build_annual_cashflows()` (L395-455), `build_economics_schedule()` (L547-652) — both embed identical hardcoded linear decline |
| `digitalmodel/src/digitalmodel/field_development/__init__.py` | — | Package init |
| `digitalmodel/src/digitalmodel/field_development/capex_estimator.py` | — | CAPEX backend (not affected) |
| `digitalmodel/src/digitalmodel/field_development/opex_estimator.py` | — | OPEX backend (not affected) |
| `digitalmodel/src/digitalmodel/field_development/concept_selection.py` | — | HostType enum (not affected) |

#### Upstream backends — `worldenergydata` (already implemented, read-only for this issue)

| File | Key Class/Function | Models |
|------|-------------------|--------|
| `worldenergydata/src/worldenergydata/production/forecast/decline.py` | `ArpsDeclineCurve`, `ForecastResult` | exponential, hyperbolic, harmonic |
| `worldenergydata/src/worldenergydata/brazil_anp/production/decline_curves.py` | `DeclineCurveAnalyzer`, `DeclineModel` enum | exponential, hyperbolic, harmonic |
| `worldenergydata/src/worldenergydata/bsee/analysis/forecasting/decline_analysis.py` | `DeclineAnalysis` | exponential, hyperbolic, harmonic + AIC selection |
| `worldenergydata/src/worldenergydata/sodir/forecasting.py` | `ProductionForecaster`, `DeclineCurve` | exponential, hyperbolic, harmonic, linear |
| `worldenergydata/src/worldenergydata/reservoir/resource_estimation.py` | `MonteCarloEngine`, `run_resource_estimation()` | OOIP → EUR via P10/P50/P90 Monte Carlo |
| `worldenergydata/src/worldenergydata/fdas/data/production.py` | `ProductionForecaster` | exponential, hyperbolic |
| `worldenergydata/src/worldenergydata/eia_us/analysis/basin_decline.py` | `arps_hyperbolic()`, `HyperbolicDeclineModel` | Arps hyperbolic with terminal switch |

### 1.2 Tests Already Present

| Test file | Count | Coverage area |
|-----------|-------|---------------|
| `digitalmodel/tests/field_development/test_economics.py` | 45 tests, 583 lines | EconomicsInput validation, adapter resolution, evaluate_economics (mocked), fiscal regime, edge cases, CashFlowSchedule, carbon sensitivity |
| `digitalmodel/tests/marine_ops/reservoir/test_modeling.py` | 9 tests | Arps decline (exponential, harmonic, hyperbolic) — separate module, not wired to economics |
| `worldenergydata/tests/unit/production/forecast/test_decline.py` | — | ArpsDeclineCurve fit/forecast tests |
| `worldenergydata/tests/unit/bsee/analysis/test_decline_analysis.py` | — | BSEE decline analysis tests |

**Key gap**: No test in `test_economics.py` exercises decline curve behavior. `_build_annual_cashflows()` is only tested implicitly via `evaluate_economics()` which uses mocked backends.

### 1.3 Current Production Profile Logic (Hardcoded — Duplicated in Two Locations)

**Location 1** — `_build_annual_cashflows()` at L420-432:
```python
plateau_years = max(1, int(n * 0.6))
# ...
if yr <= plateau_years:
    prod_factor = 1.0
else:
    decline_years = n - plateau_years
    if decline_years > 0:
        frac_decline = (yr - plateau_years) / decline_years
        prod_factor = 1.0 - 0.8 * frac_decline   # Linear: 100% → 20%
    else:
        prod_factor = 0.2
```

**Location 2** — `build_economics_schedule()` at L617-633 (identical logic).

**Behavior**: 60% of field life at full plateau → linear decline to 20% of plateau over remaining 40%.

### 1.4 `EconomicsInput` Current Fields (L75-132)

```python
@dataclass
class EconomicsInput:
    # Required
    field_name: str
    water_depth_m: float
    host_type: str
    production_capacity_bopd: float
    oil_price_usd_per_bbl: float
    discount_rate: float
    fiscal_regime: FiscalRegime
    field_life_years: int

    # Optional (existing)
    reservoir_size_mmbbl: Optional[float] = None  # L95 — placeholder, UNUSED
    opex_usd_per_bbl: Optional[float] = None
    capex_usd_mm: Optional[float] = None
    abex_usd_mm: Optional[float] = None
    carbon_cost_usd_per_tonne: Optional[float] = None
    region: Optional[str] = None
```

**Key**: `reservoir_size_mmbbl` exists at L95 but the docstring says "used for reserves-based analysis in future fiscal regime work". It is never referenced in any calculation.

### 1.5 Relevant Commits

| Hash | Date | Description |
|------|------|-------------|
| `866375922` | 2026-03-14 | `docs(WRK-1179): SEPD decline calculation report + submodule update` |
| `ee95e8c5f` | 2026-02-13 | `feat(work-queue): complete WRK-077 decline curve analysis, update submodule` |
| (economics.py header) | — | `# ABOUTME: Issue #1858 — NPV/IRR/MIRR evaluation, CAPEX/OPEX/ABEX adapter layer.` |

No commits reference issue #2054. The feature is entirely unimplemented.

---

## 2. Remaining Implementation Delta

### 2.1 Exact Missing Behaviors

| # | Behavior | Status |
|---|----------|--------|
| 1 | `EconomicsInput` accepts optional `decline_rate: float` | MISSING |
| 2 | `EconomicsInput` accepts optional `decline_type: str` (exponential / hyperbolic / harmonic) | MISSING |
| 3 | `__post_init__` validates `decline_type` against allowed values | MISSING |
| 4 | `__post_init__` validates `decline_rate` is in (0, 1] when provided | MISSING |
| 5 | `_build_annual_cashflows()` uses Arps exponential/hyperbolic/harmonic decline when params provided | MISSING — hardcoded linear |
| 6 | `build_economics_schedule()` uses same Arps decline (duplicated logic) | MISSING — hardcoded linear |
| 7 | `reservoir_size_mmbbl` used for EUR-based decline parameterization | MISSING — field exists but unused |
| 8 | Fallback to current linear model when no decline params provided | TRIVIALLY SATISFIED — current code is the fallback |
| 9 | Shared production-profile helper to eliminate duplication between `_build_annual_cashflows()` and `build_economics_schedule()` | NOT REQUIRED but strongly recommended |

### 2.2 Exact File Paths That Should Change

| File | Nature of change |
|------|-----------------|
| `digitalmodel/src/digitalmodel/field_development/economics.py` | Add `decline_rate`, `decline_type` to `EconomicsInput`; add `DeclineType` enum; refactor `_build_annual_cashflows()` and `build_economics_schedule()` production profile logic; optionally extract shared `_production_profile()` helper |
| `digitalmodel/tests/field_development/test_economics.py` | Add decline curve tests: exponential, hyperbolic, harmonic, fallback, validation, EUR-based |
| `worldenergydata` submodule | NO CHANGES NEEDED — backends already exist |

### 2.3 Recommended Integration Path

Use **pure Arps math inline** rather than importing a worldenergydata class. Rationale:

1. The economics module needs annual prod_factor values (0.0–1.0), not monthly bbl/day forecasts
2. The Arps formulas are 3 one-liners: `qi * exp(-D*t)`, `qi / (1+b*D*t)^(1/b)`, `qi / (1+D*t)`
3. Avoids adding scipy/pandas dependencies to the screening-level evaluator
4. The existing worldenergydata `ArpsDeclineCurve` fits historical data — this use case generates synthetic forward profiles from user-supplied parameters

If the team prefers delegating to worldenergydata, the cleanest target is:
```python
from worldenergydata.production.forecast.decline import ArpsDeclineCurve, ForecastResult
```

---

## 3. TDD-First Execution Plan

### 3.1 Failing Tests to Add First

Add to `digitalmodel/tests/field_development/test_economics.py`:

```python
# --- Phase 1: Input validation tests ---

class TestDeclineCurveInput:
    def test_decline_type_exponential_accepted(self, minimal_input):
        """EconomicsInput accepts decline_type='exponential'."""

    def test_decline_type_hyperbolic_accepted(self, minimal_input):
        """EconomicsInput accepts decline_type='hyperbolic'."""

    def test_decline_type_harmonic_accepted(self, minimal_input):
        """EconomicsInput accepts decline_type='harmonic'."""

    def test_invalid_decline_type_raises(self, minimal_input):
        """Unknown decline_type raises ValueError."""

    def test_decline_rate_zero_raises(self):
        """decline_rate=0 raises ValueError."""

    def test_decline_rate_negative_raises(self):
        """decline_rate < 0 raises ValueError."""

    def test_decline_type_without_rate_raises(self):
        """decline_type without decline_rate is invalid."""

    def test_decline_rate_without_type_defaults_exponential(self):
        """decline_rate alone defaults decline_type to 'exponential'."""


# --- Phase 2: Production profile shape tests ---

class TestDeclineCurveProfiles:
    def test_exponential_decline_first_year_is_plateau(self):
        """Year 1 prod_factor is 1.0 during plateau."""

    def test_exponential_decline_shape_monotonic(self):
        """Exponential decline produces monotonically decreasing profile."""

    def test_hyperbolic_decline_slower_than_exponential(self):
        """Hyperbolic decline (b>0) declines more slowly than exponential."""

    def test_harmonic_decline_b_equals_one(self):
        """Harmonic is hyperbolic with b=1."""

    def test_fallback_to_linear_when_no_params(self):
        """Without decline_rate/type, behavior matches current linear model."""

    def test_npv_changes_with_decline_type(self):
        """Different decline types produce different NPVs for same field."""


# --- Phase 3: EUR-based parameterization ---

class TestEURDeclineParameterization:
    def test_reservoir_size_sets_eur_target(self):
        """reservoir_size_mmbbl constrains total produced volume."""

    def test_eur_based_decline_respects_field_life(self):
        """EUR-based curve fits within field_life_years."""


# --- Phase 4: Schedule integration ---

class TestDeclineCurveSchedule:
    def test_schedule_uses_decline_curve(self):
        """build_economics_schedule() uses decline params when provided."""

    def test_schedule_fallback_matches_old_behavior(self):
        """Schedule without decline params matches pre-#2054 output."""
```

### 3.2 Implementation Steps (After Tests Fail)

**Step 1 — Add `DeclineType` enum and `EconomicsInput` fields** (economics.py L60-68):
```python
class DeclineType(Enum):
    EXPONENTIAL = "exponential"
    HYPERBOLIC = "hyperbolic"
    HARMONIC = "harmonic"
```

Add to `EconomicsInput` after L102:
```python
    decline_type: Optional[str] = None   # "exponential" | "hyperbolic" | "harmonic"
    decline_rate: Optional[float] = None  # annual nominal decline rate (0, 1]
    b_factor: Optional[float] = None      # hyperbolic exponent, default 0.5 for hyperbolic
```

Add validation in `__post_init__` after L131.

**Step 2 — Extract `_production_factors()` helper**:
```python
def _production_factors(
    field_life_years: int,
    plateau_fraction: float = 0.6,
    decline_type: Optional[str] = None,
    decline_rate: Optional[float] = None,
    b_factor: float = 0.5,
) -> list[float]:
    """Return per-year production factors [0..n] where year 0 = 0.0 (pre-production)."""
```

This eliminates the duplication between `_build_annual_cashflows()` and `build_economics_schedule()`.

**Step 3 — Wire `_production_factors()` into both functions**.

**Step 4 — Add EUR-based parameterization** (optional, if `reservoir_size_mmbbl` is provided without `decline_rate`):
- Derive `decline_rate` such that cumulative production ≈ EUR within field life
- Formula: for exponential, `D = -ln(q_limit/qi) / t_decline`

### 3.3 Verification Commands

```bash
# 1. Run economics tests only
cd digitalmodel && uv run pytest tests/field_development/test_economics.py -v

# 2. Run with coverage to verify new branches hit
cd digitalmodel && uv run pytest tests/field_development/test_economics.py --cov=digitalmodel.field_development.economics --cov-report=term-missing

# 3. Verify backward compatibility — existing tests must still pass
cd digitalmodel && uv run pytest tests/field_development/ -v

# 4. Import check — ensure no new heavy dependencies
cd digitalmodel && uv run python -c "from digitalmodel.field_development.economics import EconomicsInput, DeclineType; print('OK')"

# 5. Smoke test — exponential decline produces valid NPV
cd digitalmodel && uv run python -c "
from digitalmodel.field_development.economics import EconomicsInput, FiscalRegime, evaluate_economics
inp = EconomicsInput(
    field_name='Test', water_depth_m=1200.0, host_type='TLP',
    production_capacity_bopd=80000, oil_price_usd_per_bbl=70.0,
    discount_rate=0.10, fiscal_regime=FiscalRegime.US,
    field_life_years=20, decline_type='exponential', decline_rate=0.15,
)
r = evaluate_economics(inp)
print(f'NPV={r.metrics.npv_usd_mm:.1f} MM USD')
"

# 6. Backward compat — no decline params gives same result as before
cd digitalmodel && uv run python -c "
from digitalmodel.field_development.economics import EconomicsInput, FiscalRegime, evaluate_economics
inp = EconomicsInput(
    field_name='Test', water_depth_m=1200.0, host_type='TLP',
    production_capacity_bopd=80000, oil_price_usd_per_bbl=70.0,
    discount_rate=0.10, fiscal_regime=FiscalRegime.US,
    field_life_years=20,
)
r = evaluate_economics(inp)
print(f'NPV={r.metrics.npv_usd_mm:.1f} MM USD (should match pre-change baseline)')
"
```

---

## 4. Risk / Blocker Analysis

### 4.1 Plan-Gate Blockers

| Blocker | Severity | Mitigation |
|---------|----------|------------|
| Issue #2054 lacks `status:plan-approved` label | **BLOCKING** | User must review this dossier, then apply `status:plan-approved` to unblock implementation |
| AGENTS.md requires plan → approval → implementation flow | **BLOCKING** | This dossier serves as the plan; approval unlocks next step |

### 4.2 Data / Source Dependencies

| Dependency | Risk | Notes |
|------------|------|-------|
| `worldenergydata` submodule version | LOW | If inline Arps math is used, no new worldenergydata dependency. If `ArpsDeclineCurve` is imported, the class already exists in current submodule |
| `scipy` dependency | LOW | Only needed if fitting historical data; for synthetic forward profiles, pure numpy suffices |
| `reservoir_size_mmbbl → EUR` mapping | MEDIUM | The EUR-based parameterization (behavior #7) requires deciding: does `reservoir_size_mmbbl` represent OOIP or EUR directly? Issue body says "EUR-based decline curve parameterization" — suggests it's OOIP and needs a recovery factor. Needs clarification or a default RF (0.10–0.35 typical offshore) |

### 4.3 Merge / Contention Concerns

| Concern | Risk | Notes |
|---------|------|-------|
| Parallel work on `economics.py` | LOW | No other open issues target this file currently |
| `build_economics_schedule()` shares decline logic | MEDIUM | Must update BOTH functions or extract shared helper — easy to miss one |
| `EconomicsInput` field ordering | LOW | New optional fields go after existing optionals — no positional breakage since all optional fields use keyword args |
| `worldenergydata` submodule pin | LOW | No submodule changes needed for inline math approach |

---

## 5. Ready-to-Execute Prompt

```
You are implementing GitHub issue #2054: feat(field-dev): add production decline curve to economics cashflow model.

## Context
- File: digitalmodel/src/digitalmodel/field_development/economics.py (693 lines)
- Test: digitalmodel/tests/field_development/test_economics.py (583 lines)
- The `_build_annual_cashflows()` (L395) and `build_economics_schedule()` (L617) both
  contain identical hardcoded linear decline logic (60% plateau → linear to 20%).
- `EconomicsInput` (L75-132) has `reservoir_size_mmbbl` but no decline parameters.

## Requirements
1. Add `DeclineType` enum: exponential, hyperbolic, harmonic
2. Add to `EconomicsInput`:
   - `decline_type: Optional[str] = None`
   - `decline_rate: Optional[float] = None` (annual nominal, (0,1])
   - `b_factor: Optional[float] = None` (hyperbolic exponent, default 0.5)
3. Add `__post_init__` validation:
   - `decline_type` must be in DeclineType values if provided
   - `decline_rate` must be in (0, 1] if provided
   - `decline_type` without `decline_rate` raises ValueError
   - `decline_rate` without `decline_type` defaults to exponential
4. Extract `_production_factors(n, plateau_fraction, decline_type, decline_rate, b_factor)`
   to eliminate duplication between the two functions
5. Arps formulas (time t in years after plateau):
   - Exponential: prod_factor = exp(-D * t)
   - Hyperbolic: prod_factor = (1 + b * D * t) ** (-1/b)
   - Harmonic: prod_factor = 1 / (1 + D * t)
6. When no decline params: fall back to current linear (backward compat)
7. When `reservoir_size_mmbbl` provided without `decline_rate`: derive rate such that
   cumulative ≈ EUR (assume recovery_factor=0.15 default)
8. Update both `_build_annual_cashflows()` and `build_economics_schedule()` to use
   `_production_factors()`

## TDD Protocol
Write failing tests first, then implement. Tests must cover:
- Input validation (3 valid types, invalid type, rate bounds, combined params)
- Profile shapes (monotonic decline, exponential < hyperbolic, harmonic = b=1)
- Backward compat (no params → identical to pre-change)
- EUR-based (reservoir_size constrains total production)
- Schedule integration (build_economics_schedule uses decline)

## Verification
```bash
cd digitalmodel && uv run pytest tests/field_development/test_economics.py -v
cd digitalmodel && uv run pytest tests/field_development/ -v
cd digitalmodel && uv run python -c "from digitalmodel.field_development.economics import DeclineType; print(list(DeclineType))"
```

## Cross-Review
After implementation, run code review per AGENTS.md cross-review policy.
Commit message: feat(field-dev): add Arps decline curves to economics cashflow model (#2054)
```

---

## 6. Architectural Notes

### Why Inline Math Over worldenergydata Import

The `ArpsDeclineCurve` class in `worldenergydata/production/forecast/decline.py` is designed for **fitting historical production data** — it takes a DataFrame of monthly actuals and returns fitted parameters. Issue #2054 needs the **inverse**: given user-supplied `decline_rate` and `decline_type`, generate annual production factors. The three Arps formulas are trivial one-liners in numpy:

```python
# Exponential: q(t) = qi * exp(-D*t)
factors = np.exp(-decline_rate * t_after_plateau)

# Hyperbolic: q(t) = qi * (1 + b*D*t)^(-1/b)
factors = (1 + b * decline_rate * t_after_plateau) ** (-1.0 / b)

# Harmonic: q(t) = qi / (1 + D*t)
factors = 1.0 / (1 + decline_rate * t_after_plateau)
```

Adding a `from worldenergydata.production.forecast.decline import ...` for this would be over-engineering. The facade pattern in `economics.py` delegates to worldenergydata for **complex backends** (cost prediction ML, decommissioning estimation, DCF analysis) — decline math doesn't qualify.

### Duplication Elimination

The production profile logic appears identically in two places:
- `_build_annual_cashflows()` (L420-432) — returns `np.ndarray` of net cashflows
- `build_economics_schedule()` (L617-633) — returns `CashFlowSchedule` dataclass

A shared `_production_factors()` function eliminates this. Both callers would use:
```python
factors = _production_factors(inp.field_life_years, 0.6, inp.decline_type, inp.decline_rate, inp.b_factor)
```

---

## 7. Final Recommendation

**READY AFTER LABEL UPDATE**

Issue #2054 is well-scoped, the upstream backends are already in place, and the implementation is confined to a single file with a clear test strategy. The feature requires:
- 1 file changed: `digitalmodel/src/digitalmodel/field_development/economics.py`
- 1 test file changed: `digitalmodel/tests/field_development/test_economics.py`
- ~60-80 lines of new production code + ~120 lines of new tests
- Zero worldenergydata submodule changes

**Action needed**: Apply `status:plan-approved` label to issue #2054, then dispatch implementation agent with the ready-to-execute prompt in Section 5.
