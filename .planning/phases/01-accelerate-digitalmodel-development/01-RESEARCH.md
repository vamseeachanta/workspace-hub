# Phase 1: Accelerate digitalmodel development - Research

**Researched:** 2026-03-25
**Domain:** Python engineering calculation modules -- offshore structural, fatigue, CP, VIV, pipeline
**Confidence:** HIGH

## Summary

digitalmodel is a mature Python monorepo with 30+ engineering sub-modules spanning structural analysis, subsea engineering, hydrodynamics, and marine operations. The codebase has well-established patterns for standard-to-code implementation: one Python file per standard, constants traced to section/table numbers in docstrings, and a `CodeStrategy` Protocol + `@register_code` decorator for pluggable design code checks. The cathodic protection module (`dnv_rp_b401.py`) and wall thickness codes (`wall_thickness_codes/`) are the gold-standard templates for new module development.

The module registry (`specs/module-registry.yaml`) documents specific gaps that align with the phase goal. The highest-value candidates for new modules are: (1) on-bottom stability (DNV-RP-F109) -- a complete new domain capability with no existing code, (2) spectral fatigue from irregular wave loading -- extending the already-production-quality fatigue module, and (3) straked suppression / enhanced VIV screening -- extending the existing VIV analysis module. These three hit the UAT target of "3+ new calculation modules with full test coverage and traceability." Alternative candidates include ASME B31.4 wall thickness (extending existing multi-code pattern) and biaxial stress interaction correction.

The critical constraint is D-03/D-04: new modules must have self-contained test suites that work independently. The legacy test infrastructure issue (0/150 runnable in structural/analysis) is explicitly out of scope. The cathodic protection test suite (`tests/cathodic_protection/`) is the proven template -- each test references source document sections and expected values, uses `pytest.approx` for numerical tolerance, and imports directly from the module without shared fixtures.

**Primary recommendation:** Build 3 new modules following the established one-file-per-standard pattern with self-contained pytest suites. Prioritize on-bottom stability (new domain), spectral fatigue (high-value extension), and one additional module selected from the gap pool based on available standard references.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Use module registry gaps (`specs/module-registry.yaml`) as the starting pool, but filter through market signal before committing -- competitor analysis (Sesam, SACS, Flexcom), industry demand patterns, and engineering judgment of what offshore clients actually need.
- **D-02:** The registry already documents specific gaps: spectral fatigue, SHEAR7/VIVA VIV, on-bottom stability, biaxial stress interaction, straked suppression. These are the candidate pool.
- **D-03:** New modules get self-contained test suites that work independently. Do NOT block new module development on fixing legacy test infrastructure (0/150 runnable in structural/analysis).
- **D-04:** Legacy test fixes (import path issues, TEST_STATUS_DASHBOARD blockers) are a separate effort, not a prerequisite for this phase.
- **D-05:** Dual traceability -- docstrings for developer readability (continue existing pattern: "DNV-RP-B401 S7.4.1, Eq 1") PLUS a per-module YAML manifest for CI validation and website showcase.
- **D-06:** YAML manifest per module should map each function to its standard, clause, equation number, and edition -- machine-readable and CI-validatable.
- **D-07:** "New calculation module" for UAT can be either a new standard implementation (e.g., adding ASME B31.4 to wall thickness) OR a new domain capability (e.g., on-bottom stability). Mix is acceptable. 3+ total.
- **D-08:** New modules use `assetutilities` for shared infrastructure (config, calculations, base solvers) via the existing editable path dependency. No duplication.

### Claude's Discretion
- Exact order of which 3+ modules to build (within the validated gap pool)
- YAML manifest schema design
- Test framework choice for new module suites (pytest assumed)

### Deferred Ideas (OUT OF SCOPE)
- Legacy test infrastructure fix (0/150 structural/analysis tests) -- separate effort
- Client feedback system / CRM integration -- Phase 4
- DNV-RP-F105 edition update check -- nightly research (Phase 5)
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.11 | Runtime (configured in `uv.toml`) | Project standard |
| pytest | >=7.4.3,<9.0.0 | Test framework | Already configured in `pyproject.toml` and `pytest.ini` |
| numpy | >=1.24.0,<2.0.0 | Numerical arrays for engineering calculations | Already a dependency |
| scipy | >=1.10.0,<2.0.0 | Special functions, integration, interpolation | Already a dependency; needed for spectral methods |
| pydantic | >=2.7.0,<3.0.0 | Data models for YAML manifest validation | Already a dependency |
| pyyaml | >=6.0.0,<7.0.0 | YAML manifest read/write | Already a dependency |
| rainflow | >=3.2.0,<4.0.0 | Cycle counting for fatigue analysis | Already a dependency |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-cov | >=4.1.0,<5.0.0 | Coverage measurement per module | Every new test suite |
| hypothesis | >=6.100.0,<7.0.0 | Property-based testing for edge cases | Numerical correctness validation |
| uncertainties | ==3.1.7 | Error propagation | When standard specifies tolerance bands |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Raw dict for manifest | Pydantic model | Pydantic provides validation + JSON Schema export for CI; use it |
| Hand-rolled YAML schema | JSON Schema from Pydantic | Pydantic `model_json_schema()` auto-generates; no hand-rolling |

**Installation:** All dependencies already present in `pyproject.toml`. No new packages needed.

## Architecture Patterns

### Recommended Project Structure for a New Module

```
src/digitalmodel/{domain}/{module_name}/
    __init__.py              # Public API exports
    {standard_code}.py       # One file per standard (e.g., dnv_rp_f109.py)
    manifest.yaml            # D-05/D-06: Per-module traceability manifest

tests/{domain}/{module_name}/
    __init__.py
    conftest.py              # Module-specific fixtures (self-contained per D-03)
    test_{standard_code}.py  # Tests per standard, referencing worked examples
```

### Pattern 1: One-File-Per-Standard with Docstring Traceability
**What:** Each standard gets its own Python file. Constants are module-level with section references in comments. Functions cite equation numbers in docstrings.
**When to use:** Every new standard implementation.
**Example (from existing `dnv_rp_b401.py`):**
```python
# Protection potentials vs Ag/AgCl (DNV-RP-B401 S5.4.1)
PROTECTION_POTENTIAL_AGAGCL: float = -0.800  # V vs Ag/AgCl

def current_demand(
    surface_area_m2: float,
    current_density_A_m2: float,
    breakdown_factor: float,
) -> float:
    """Current demand for a coated structure (DNV-RP-B401 S7.4.1, Eq 1).

    I_c = A_c * i_c * f_c
    """
    return surface_area_m2 * current_density_A_m2 * breakdown_factor
```

### Pattern 2: CodeStrategy Protocol + Registry (for multi-code domains)
**What:** A `Protocol` defines the interface, a `@register_code` decorator auto-registers implementations, and a `CODE_REGISTRY` dict enables runtime dispatch.
**When to use:** When multiple standards solve the same problem (e.g., wall thickness per DNV/API/ASME). On-bottom stability could use this if multiple codes are planned.
**Example (from existing `wall_thickness_codes/base.py`):**
```python
@runtime_checkable
class CodeStrategy(Protocol):
    code_name: str
    check_names: List[str]
    def run_checks(self, geometry, material, loads, factors) -> Dict[str, Tuple[float, Dict]]: ...

CODE_REGISTRY: Dict[DesignCode, type] = {}

def register_code(code_enum: DesignCode):
    def decorator(cls):
        CODE_REGISTRY[code_enum] = cls
        return cls
    return decorator
```

### Pattern 3: Self-Contained Test Suite with Document Verification
**What:** Tests reference specific sections of engineering documents. Each test class covers one calculation function. `pytest.approx` handles numerical tolerance.
**When to use:** Every new module test suite (per D-03).
**Example (from existing `test_dnv_rp_b401_doc_verified.py`):**
```python
class TestCurrentDemand:
    """Verify current demand I_c = A_c * i_c * f_c (DNV-RP-B401 S7.4.1)."""

    def test_buoyancy_tank_initial_current_demand(self):
        """Verify against hybrid riser CP design report S5.1.1."""
        result = current_demand(
            surface_area_m2=1021.0,
            current_density_A_m2=0.440,
            breakdown_factor=0.02,
        )
        assert result == pytest.approx(8.98, abs=0.05)
```

### Pattern 4: YAML Manifest for CI Traceability (NEW -- per D-05/D-06)
**What:** Machine-readable YAML file per module mapping functions to standards/clauses/equations.
**When to use:** Every new module (and retrofittable to existing modules later).
**Recommended schema:**
```yaml
module: subsea/on_bottom_stability
standard: DNV-RP-F109
edition: 2021
functions:
  - name: absolute_stability_check
    clause: "S4.3.1"
    equation: "Eq 4.1"
    description: "Absolute lateral stability -- pipe weight vs hydrodynamic loads"
  - name: generalized_stability_check
    clause: "S4.3.2"
    equation: "Eq 4.5"
    description: "Generalized lateral stability with soil resistance"
```

### Anti-Patterns to Avoid
- **Importing from legacy marine_engineering paths:** Use canonical `digitalmodel.{domain}.{module}` imports. The TEST_STATUS_DASHBOARD shows broken imports cause cascade failures.
- **Shared test fixtures across modules:** Each module's test suite must be self-contained (D-03). Do not add fixtures to the root `conftest.py`.
- **Duplicating assetutilities infrastructure:** Use `from assetutilities.calculation import ...` or `from assetutilities.math_helpers import ...` (D-08).
- **Building a monolithic "standards library":** Keep one file per standard. Do not merge multiple standards into a single file.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Rainflow cycle counting | Custom implementation | `rainflow` library (already in deps) | ASTM E1049-85 compliant, battle-tested |
| Spectral density integration | Manual trapezoidal | `scipy.integrate.trapezoid` / `scipy.signal` | Numerical edge cases in spectral tails |
| YAML manifest validation | Custom dict checks | Pydantic model with `model_json_schema()` | Auto-generates JSON Schema for CI |
| Unit conversions | Inline conversion factors | `assetutilities.units` | Centralized, tested, covers offshore units |
| Wave spectrum generation | New spectrum functions | Existing `hydrodynamics/wave_spectra.py` | JONSWAP/PM already implemented |
| S-N curve lookup | New curve database | Existing `structural/fatigue/` (221 curves) | Production maturity, 17 standards |

**Key insight:** digitalmodel already has substantial infrastructure. New modules should compose existing building blocks, not rebuild them.

## Common Pitfalls

### Pitfall 1: Import Path Inconsistency
**What goes wrong:** Tests fail with `ModuleNotFoundError` because import paths don't match the installed package structure.
**Why it happens:** The package uses `src/` layout with `setuptools.packages.find(where=["src"])`. Relative imports or ad-hoc `sys.path` manipulation breaks.
**How to avoid:** Always use absolute imports: `from digitalmodel.subsea.on_bottom_stability.dnv_rp_f109 import ...`. Run `uv pip install -e .` before testing.
**Warning signs:** Tests pass locally with `PYTHONPATH` hack but fail in CI.

### Pitfall 2: Numerical Precision in Standard Equations
**What goes wrong:** Tests fail because hand-calculated expected values don't match code output due to intermediate rounding.
**Why it happens:** Engineering standards often show rounded intermediate values in worked examples. Code computes full precision.
**How to avoid:** Use `pytest.approx(expected, abs=tolerance)` with tolerance documented and justified. Source the expected value from the standard's worked example, not from hand calculation.
**Warning signs:** Tests with `== exact_value` comparisons on floating-point results.

### Pitfall 3: Unit Confusion Between Standards
**What goes wrong:** A function produces wrong results because input units don't match what the standard assumes.
**Why it happens:** Different standards use different unit conventions (e.g., DNV uses SI, API uses mixed imperial).
**How to avoid:** Document input/output units in every function signature. Use typed parameter names with units (e.g., `pressure_MPa`, `depth_m`). Consider Pydantic models with unit validation for complex inputs.
**Warning signs:** Dimensional analysis of equation inputs doesn't balance.

### Pitfall 4: Edition-Dependent Factors
**What goes wrong:** Code produces wrong safety factors because it uses the wrong edition of a standard.
**Why it happens:** Standards revise safety factors between editions (see `dnv_st_f101.py` with 2007 vs 2021 gamma_SC values).
**How to avoid:** Follow the existing `EDITION_FACTORS` pattern. Make edition a required or defaulted parameter. Document which edition values come from.
**Warning signs:** Results don't match client's spreadsheet because they use a different edition.

### Pitfall 5: Conftest Pollution Breaking Self-Containment
**What goes wrong:** A new module's tests pass alone but break when run with the full suite, or vice versa.
**Why it happens:** Root `conftest.py` has `collect_ignore` entries and shared state. Fixtures from one module leak into another.
**How to avoid:** Each module test directory gets its own `conftest.py`. Do not add fixtures to the root `conftest.py`. Run `pytest tests/{domain}/{module}/` in isolation during development.
**Warning signs:** Test results differ between `pytest tests/subsea/on_bottom_stability/` and `pytest tests/`.

## Code Examples

### New Module File Template
```python
"""DNV-RP-F109 -- On-Bottom Stability Design (2021).

Implements pipeline on-bottom stability checks including absolute lateral
stability, generalized lateral stability with soil resistance, and
vertical stability (uplift).
"""

from __future__ import annotations

import math
from typing import NamedTuple


class StabilityResult(NamedTuple):
    """Result of a stability check."""
    utilisation: float  # demand / capacity ratio
    is_stable: bool     # utilisation <= 1.0
    details: dict       # intermediate values for audit trail


# ---------------------------------------------------------------------------
# Hydrodynamic coefficients (DNV-RP-F109 Table 3-3)
# ---------------------------------------------------------------------------
C_D_SMOOTH: float = 0.9   # Drag coefficient, smooth pipe
C_L_SMOOTH: float = 0.9   # Lift coefficient, smooth pipe
C_M_SMOOTH: float = 3.29  # Inertia coefficient, smooth pipe

C_D_ROUGH: float = 1.2    # Drag coefficient, rough pipe (marine growth)
C_L_ROUGH: float = 1.0    # Lift coefficient, rough pipe
C_M_ROUGH: float = 3.29   # Inertia coefficient, rough pipe


def hydrodynamic_force_per_meter(
    rho_w_kg_m3: float,
    D_outer_m: float,
    U_m_s: float,
    a_m_s2: float,
    C_D: float = C_D_SMOOTH,
    C_M: float = C_M_SMOOTH,
) -> float:
    """Inline hydrodynamic force per unit length (DNV-RP-F109 S3.2.1, Eq 3.1).

    F_H = 0.5 * rho * C_D * D * |U| * U + rho * C_M * (pi/4) * D^2 * a

    Parameters
    ----------
    rho_w_kg_m3 : float
        Seawater density [kg/m3].
    D_outer_m : float
        Outer pipe diameter including coatings [m].
    U_m_s : float
        Combined current + wave velocity at pipe [m/s].
    a_m_s2 : float
        Combined current + wave acceleration at pipe [m/s2].

    Returns
    -------
    float
        Horizontal hydrodynamic force per meter [N/m].
    """
    drag = 0.5 * rho_w_kg_m3 * C_D * D_outer_m * abs(U_m_s) * U_m_s
    inertia = rho_w_kg_m3 * C_M * (math.pi / 4) * D_outer_m**2 * a_m_s2
    return drag + inertia
```

### New Module Test Template
```python
"""Tests for DNV-RP-F109 on-bottom stability module.

All expected values sourced from DNV-RP-F109 worked examples or
independently verified engineering calculations with traceability.
"""
from __future__ import annotations

import pytest

from digitalmodel.subsea.on_bottom_stability.dnv_rp_f109 import (
    hydrodynamic_force_per_meter,
    C_D_SMOOTH,
    C_M_SMOOTH,
)


class TestHydrodynamicForce:
    """Verify hydrodynamic force per DNV-RP-F109 S3.2.1."""

    def test_zero_velocity_zero_force(self):
        """No flow means no hydrodynamic force."""
        result = hydrodynamic_force_per_meter(
            rho_w_kg_m3=1025.0, D_outer_m=0.5, U_m_s=0.0, a_m_s2=0.0,
        )
        assert result == pytest.approx(0.0, abs=1e-6)

    def test_pure_drag_force(self):
        """Steady current (no acceleration) -- drag only."""
        result = hydrodynamic_force_per_meter(
            rho_w_kg_m3=1025.0, D_outer_m=0.5, U_m_s=1.0, a_m_s2=0.0,
        )
        expected_drag = 0.5 * 1025.0 * C_D_SMOOTH * 0.5 * 1.0 * 1.0
        assert result == pytest.approx(expected_drag, rel=1e-6)
```

### YAML Manifest Template
```yaml
# manifest.yaml -- Machine-readable traceability for CI and website
module: subsea/on_bottom_stability
description: "Pipeline on-bottom stability design per DNV-RP-F109"
primary_standard:
  id: DNV-RP-F109
  edition: 2021
  title: "On-Bottom Stability Design of Submarine Pipelines"
functions:
  - name: hydrodynamic_force_per_meter
    clause: "S3.2.1"
    equation: "Eq 3.1"
    description: "Inline hydrodynamic force per unit length"
    inputs: [rho_w_kg_m3, D_outer_m, U_m_s, a_m_s2, C_D, C_M]
    outputs: [force_N_per_m]
  - name: absolute_stability_check
    clause: "S4.3.1"
    equation: "Eq 4.1"
    description: "Absolute lateral stability check"
    inputs: [submerged_weight_N_m, F_H_N_m, F_L_N_m, mu_soil]
    outputs: [StabilityResult]
```

## Gap Analysis and Module Recommendations

Based on the registry gaps (D-02) and market signal considerations (D-01):

### Tier 1: Highest Value (recommended for 3-module UAT)

| Gap | Module Path | Standard | Type | Rationale |
|-----|-------------|----------|------|-----------|
| On-bottom stability | `subsea/on_bottom_stability/` | DNV-RP-F109 | New domain | Every pipeline project needs it; Sesam/SACS have it; digitalmodel does not |
| Spectral fatigue (sea-state scatter) | `structural/fatigue/` (extend) | DNV-RP-C203 Appendix C/D | Extension | Most-requested fatigue method for deepwater; extends production module |
| ASME B31.4 wall thickness | `structural/analysis/wall_thickness_codes/` (extend) | ASME B31.4 | New standard | Multi-code pattern already exists; common for onshore/topsides piping |

### Tier 2: High Value (alternatives or additions)

| Gap | Module Path | Standard | Type | Rationale |
|-----|-------------|----------|------|-----------|
| Biaxial stress interaction | `structural/fatigue/` (extend) | DNV-RP-C203 S2.10 | Extension | Needed for tubular joints under multiaxial loading |
| Straked suppression VIV model | `subsea/viv_analysis/` (extend) | DNV-RP-F105 Appendix | Extension | Value-add for riser and span assessment |
| Jacket joint punching shear | `structural/structural_analysis/` (extend) | API RP 2A / ISO 19902 | Extension | Common jacket design check |

### Why This Ordering
1. **On-bottom stability** fills a complete domain gap (no existing code at all) and is needed on virtually every subsea pipeline project.
2. **Spectral fatigue** is the highest-value extension to the already-strongest module (221 S-N curves, production maturity). Frequency-domain fatigue is standard practice for deepwater.
3. **ASME B31.4** leverages the existing `CodeStrategy` / `@register_code` pattern with minimal new infrastructure -- the base class, data models, and test patterns all exist.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest >=7.4.3 (configured in pyproject.toml + pytest.ini) |
| Config file | `digitalmodel/pytest.ini` |
| Quick run command | `cd digitalmodel && uv run pytest tests/{domain}/{module}/ -x --tb=short` |
| Full suite command | `cd digitalmodel && uv run pytest tests/ --maxfail=50 -v` |

### Phase Requirements to Test Map
| Behavior | Test Type | Automated Command | File Exists? |
|----------|-----------|-------------------|-------------|
| On-bottom stability calculations | unit | `uv run pytest tests/subsea/on_bottom_stability/ -x` | Wave 0 |
| Spectral fatigue from sea-state scatter | unit | `uv run pytest tests/structural/fatigue/test_spectral_fatigue.py -x` | Wave 0 |
| New wall thickness code (ASME B31.4) | unit | `uv run pytest tests/structural/analysis/test_asme_b31_4.py -x` | Wave 0 |
| YAML manifest validates against schema | unit | `uv run pytest tests/specs/test_manifest_schema.py -x` | Wave 0 |
| Each function traces to standard clause | CI | `uv run python scripts/validate_manifests.py` | Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/{module_under_development}/ -x --tb=short`
- **Per wave merge:** `uv run pytest tests/ --maxfail=50 -v`
- **Phase gate:** Full suite green + coverage check (`--cov --cov-fail-under=80`)

### Wave 0 Gaps
- [ ] `tests/subsea/on_bottom_stability/` -- new directory + conftest.py + test files
- [ ] `tests/structural/fatigue/test_spectral_fatigue.py` -- spectral fatigue tests
- [ ] `tests/structural/analysis/test_asme_b31_4.py` -- ASME B31.4 code tests (or equivalent 3rd module)
- [ ] `tests/specs/test_manifest_schema.py` -- manifest YAML validation
- [ ] `scripts/validate_manifests.py` -- CI script to validate all manifest.yaml files against Pydantic schema

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| DNV-OS-F101 (2007) safety factors | DNV-ST-F101 (2021) revised gamma_SC | 2017-2021 | Edition-aware factor lookup already implemented |
| Time-domain only fatigue | Spectral fatigue (Dirlik, Tovo-Benasciutti) standard practice | ~2015+ industry adoption | Spectral methods now expected for deepwater screening |
| Manual stability weight calcs | DNV-RP-F109 generalized method with soil-pipe interaction | 2021 revision | Generalized method replaces absolute method for most cases |

## Open Questions

1. **Which worked examples are available for on-bottom stability?**
   - What we know: DNV-RP-F109 (2021) contains worked examples in appendices.
   - What's unclear: Whether the user has access to the standard document for test data extraction.
   - Recommendation: Plan a "data extraction" task early in the wave to source test values from the standard. If not available, use independently calculated values with documented assumptions.

2. **Spectral fatigue scope -- Dirlik only or multiple methods?**
   - What we know: The existing fatigue module already has Dirlik and Tovo-Benasciutti spectral methods implemented. The gap is the "sea-state scatter approach" -- applying these methods across a scatter diagram of sea states.
   - What's unclear: Whether this is purely a workflow/orchestration task (scatter diagram iteration + damage summation) or requires new spectral theory.
   - Recommendation: Investigate existing `structural/fatigue/` module internals to determine if the spectral engine exists and only the scatter integration is missing.

3. **YAML manifest schema -- shared across all modules or per-domain?**
   - What we know: D-06 specifies per-module manifests. Schema should be universal.
   - What's unclear: Whether existing modules will be retrofitted in this phase.
   - Recommendation: Design one Pydantic schema, ship it with the 3 new modules. Retrofitting existing modules is a separate task, deferrable.

## Project Constraints (from CLAUDE.md)

- **Retrieval first:** Consult `docs/`, `.claude/docs/`, `.claude/rules/` before training knowledge.
- **GSD framework:** Use `/gsd:*` workflow commands.
- **Edit safety:** Prefer targeted single-site edits; verify imports not mangled after edits.
- **Path handling:** Use relative paths or `$(git rev-parse --show-toplevel)` in scripts; absolute paths only in tool `file_path` parameters.
- **Agent harness files:** CLAUDE.md, MEMORY.md, AGENTS.md must not exceed 20 lines.

## Sources

### Primary (HIGH confidence)
- `digitalmodel/specs/module-registry.yaml` -- Complete gap analysis, maturity levels, standard coverage
- `digitalmodel/src/digitalmodel/cathodic_protection/dnv_rp_b401.py` -- Reference implementation pattern
- `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/base.py` -- CodeStrategy Protocol pattern
- `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/dnv_st_f101.py` -- Edition-aware implementation pattern
- `digitalmodel/tests/cathodic_protection/test_dnv_rp_b401_doc_verified.py` -- Reference test pattern
- `digitalmodel/pyproject.toml` -- Dependency versions, test configuration, coverage thresholds
- `digitalmodel/pytest.ini` -- Test markers, paths, options
- `digitalmodel/tests/conftest.py` -- Root conftest pattern (collect_ignore, known broken tests)

### Secondary (MEDIUM confidence)
- `digitalmodel/specs/data-needs.yaml` -- Data dependency tracking lifecycle
- `digitalmodel/tests/structural/analysis/TEST_STATUS_DASHBOARD.md` -- Legacy test breakage documentation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already in pyproject.toml, versions verified from source
- Architecture: HIGH -- patterns extracted from actual working code in the repository
- Pitfalls: HIGH -- pitfalls derived from documented issues (TEST_STATUS_DASHBOARD) and code inspection
- Gap prioritization: MEDIUM -- based on registry analysis and general offshore engineering knowledge; market signal validation (D-01) not performed by this research

**Research date:** 2026-03-25
**Valid until:** 2026-04-25 (stable domain -- engineering standards change slowly)
