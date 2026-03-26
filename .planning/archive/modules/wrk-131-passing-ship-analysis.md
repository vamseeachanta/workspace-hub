---
# =============================================================================
# PLAN METADATA
# =============================================================================

title: "Passing Ship Analysis for Moored Vessels"
description: "End-to-end passing ship analysis: force calculation, mooring response, parametric studies, benchmarking, and reporting — built on existing Wang formulation code."
version: "1.1"
module: "passing-ship"

session:
  id: "wrk-131-plan-v1"
  agent: "claude-opus-4-6"
  started: "2026-02-15"
  last_active: "2026-02-15"

review:
  required_iterations: 3
  current_iteration: 1
  status: "pending"
  reviewers:
    openai_codex:
      status: "pending"
      iteration: 0
    google_gemini:
      status: "pending"
      iteration: 0
    legal_sanity:
      status: "pending"
      iteration: 0
      violations: 0
  approval_gate:
    min_iterations_met: false
    codex_approved: false
    gemini_approved: false
    legal_sanity_passed: false
    ready_for_next_step: false

status: "draft"
progress: 0
phase: 0
blocked_by: []

created: "2026-02-15"
updated: "2026-02-15"
target_completion: ""
timeline: ""

technical:
  language: "python"
  python_version: ">=3.10"
  dependencies:
    - pydantic>=2.0
    - scipy
    - numpy
    - plotly
    - OrcFxAPI
    - pyyaml
    - jinja2
  test_coverage: 80
  platforms: [windows, linux, macos]

priority: "high"
complexity: "high"
risk: "medium"
tags: [passing-ship, mooring, hydrodynamics, aqwa, orcaflex, benchmark]

links:
  spec: "specs/modules/wrk-131-passing-ship-analysis.md"
  branch: ""
  pr: ""
  issues: ["WRK-131"]
  docs:
    - "acma-projects/_engineering/passing_ship/Nick Version/modPassingShip.bas"
    - "acma-projects/_engineering/passing_ship/Nick Version/PassingShipForces.pdf"
    - "acma-projects/B1512/data/passing_ship/passing_ship.md"

history:
  - date: "2026-02-15"
    action: "created"
    by: "claude-opus-4-6"
    notes: "Initial spec drafted from WRK-131 work item"
---

# Passing Ship Analysis for Moored Vessels

| Field | Value |
|-------|-------|
| Module | `passing-ship` |
| Status | Draft |
| Priority | High |
| Created | 2026-02-15 |
| Work Item | WRK-131 |

---

## Executive Summary

Build an end-to-end passing ship analysis capability for moored vessels. The system calculates hydrodynamic interaction forces (surge, sway, yaw) on a moored vessel due to a passing ship, generates force time histories for the transit event, runs mooring response analysis, supports parametric case matrices, validates against historical projects, and produces standardized HTML reports.

**Key insight**: A working Python implementation of the Wang formulation already exists at `digitalmodel/src/digitalmodel/marine_ops/marine_analysis/python_code_passing_ship/`. This plan builds on that foundation rather than starting from scratch.

### Objectives

1. Consolidate and stabilize existing passing ship force calculator (move from `marine_ops/` → `hydrodynamics/passing_ship/`)
2. Benchmark force calculator against Wang paper reference data and VBA/MathCAD implementations
3. Create `PassingShipSpec` Pydantic schema following the `DiffractionSpec` YAML pattern
4. Generate force time histories for ship transit events
5. Integrate with OrcaFlex for mooring response analysis
6. Build parametric study engine for case matrices
7. Benchmark against 5-7 historical projects
8. Generate standardized HTML reports

---

## Existing Codebase Inventory

### What Already Exists

| Component | Location | Status |
|-----------|----------|--------|
| Force calculator | `marine_ops/marine_analysis/python_code_passing_ship/calculator.py` | Working (434 lines) |
| Configuration | `python_code_passing_ship/configuration.py` | Working (424 lines) |
| Formulations (Wang) | `python_code_passing_ship/formulations.py` | Working (435 lines) |
| CLI | `python_code_passing_ship/cli.py` | Buggy (method name mismatches) |
| Visualization | `python_code_passing_ship/visualization.py` | Exists but needs verification |
| Test suite | `tests/marine_ops/.../python_code_passing_ship/` | 7 test files, MathCAD validation |

### VBA Reference (Nick Barczak, July 2016)

| File | Purpose |
|------|---------|
| `modPassingShip.bas` | Wang surge/sway/yaw + finite-depth corrections |
| `modQuadrature.bas` | Adaptive Gauss-Lobatto integration |

### What Needs To Be Built

| Component | Gap |
|-----------|-----|
| `PassingShipSpec` schema | No YAML-driven spec.yml pattern (current config is ad-hoc Pydantic) |
| Force time history | Calculator gives forces at single position, not full transit |
| Mooring response | No OrcaFlex/AQWA integration for mooring loads |
| Parametric engine | Basic `parametric_study()` exists but insufficient for case matrices |
| Benchmark suite | No historical project comparison |
| HTML reports | No reporting capability |

---

## Architecture

### Module Location

```
digitalmodel/src/digitalmodel/hydrodynamics/passing_ship/
├── __init__.py
├── input_schemas.py        # PassingShipSpec (Pydantic, YAML-driven)
├── force_calculator.py     # Refactored from existing calculator
├── formulations.py         # Wang formulations (moved from marine_ops)
├── time_history.py         # Force time history generation
├── mooring_response.py     # OrcaFlex mooring integration
├── parametric_engine.py    # Case matrix generation + batch execution
├── benchmark_runner.py     # Historical project comparison
├── report_generator.py     # HTML report output (Jinja2 + Plotly)
├── output_schemas.py       # PassingShipResults (unified output)
├── cli.py                  # Command-line interface
└── templates/
    ├── spec_template.yml   # Example spec file
    └── report_template.html
```

### Data Flow

```
PassingShipSpec (spec.yml)
    ↓
ForceCalculator.calculate_transit()
    ↓
ForceTimeHistory (surge/sway/yaw vs time)
    ↓ [if mooring analysis requested]
MooringResponse.run() → OrcaFlex time-domain
    ↓
PassingShipResults
    ↓ [if parametric]
ParametricEngine.run_matrix()
    ↓
ReportGenerator.generate()
    ↓
HTML Report
```

### Key Design Decisions

1. **Consolidate into `hydrodynamics/passing_ship/`** — Move existing `marine_ops/marine_analysis/python_code_passing_ship/` into `hydrodynamics/passing_ship/`. Delete the old location after migration. No parallel modules — single source of truth.
2. **Follow DiffractionSpec pattern** — YAML-driven, Pydantic v2, `from_yaml()`/`to_yaml()` methods.
3. **Preserve existing formulations** — Wang formulations are validated. Refactor in place, don't rewrite.
4. **OrcaFlex for mooring response** — OrcaFlex is the primary mooring solver. AQWA mooring is secondary/future.
5. **Wang paper benchmarking** — Validate force calculator against Wang's published examples before building further.

---

## Implementation Phases

### Phase 1: Consolidate Module, Fix Bugs & Benchmark Against Wang Paper

**Objective**: Consolidate the existing code into `hydrodynamics/passing_ship/`, fix known bugs, and validate against Wang's published reference data.

#### 1a. Module Consolidation (Staged Migration)

- [ ] Move `marine_ops/marine_analysis/python_code_passing_ship/` → `hydrodynamics/passing_ship/`
- [ ] Move tests from `tests/marine_ops/.../python_code_passing_ship/` → `tests/hydrodynamics/passing_ship/`
- [ ] Update all internal imports to new package path
- [ ] Scan for stale references in YAML configs, CI scripts, docs, `__init__.py` re-exports
- [ ] Add temporary import compatibility shim at old location (re-export with deprecation warning)
- [ ] Investigate ghost `python_mathcad` import in `test_mathcad_validation.py` — fix or remove
- [ ] Verify no other code imports from the old location
- [ ] Remove old directory + shim after all tests pass at new location (same Phase, not deferred)

#### 1b. Bug Fixes

- [ ] Run existing test suite, identify failures
- [ ] Fix CLI bugs: `from_config()` → `from_config_file()`, `.calculate()` → `.calculate_forces()`
- [ ] Verify visualization module exists and works
- [ ] Fix any import errors from consolidation

#### 1c. Sign Convention & Unit System Documentation

Before benchmarking, establish canonical conventions to avoid the unit/sign traps identified in review.

- [ ] Document sign conventions for all coordinate systems:

| System | +x | +y | +yaw | Notes |
|--------|----|----|------|-------|
| Wang paper | Fwd (bow) | Starboard | Clockwise (bow-to-starboard) | Verify from paper |
| VBA (`modPassingShip.bas`) | Same as Wang | Same as Wang | Same as Wang | Verify from code |
| Python (`formulations.py`) | — | — | — | Document current |
| OrcaFlex | Fwd | Starboard | Clockwise | OrcFxAPI convention |
| AQWA | Fwd | Port | Counter-clockwise | AQWA convention |

- [ ] Document unit system strategy:
  - **Benchmark reference data**: Imperial (ft, slug/ft³, lbf) — as published in Wang/MathCAD
  - **Python calculator**: SI internally (m, kg/m³, N) — convert at boundaries
  - **PassingShipSpec schema**: SI (m, kg/m³, N) — user-facing
  - **Tests**: Use both unit systems with explicit conversion to catch mismatches
- [ ] Define dimensionless normalization for cross-system comparison:
  - Force coefficient: `C_F = F / (ρ × U² × A₁ × A₂ / L₁²)`
  - Document which `L` (L₁ = moored vessel) is reference length

#### 1d. Wang Paper Benchmarking

Validate Python implementation against Wang's published reference calculations and the VBA/MathCAD implementations.

**Reference sources** (with provenance):
- Wang, S. (1975). "Hydrodynamic Forces on a Vessel Moving Along a Bank or in a Narrow Channel." *Journal of Ship Research*, Vol. 19, No. 4, pp. 200-213. (Verify exact citation from MathCAD PDFs)
- MathCAD PDF: `digitalmodel/docs/modules/ship-design/passing_ship/Calculation of forces and moments from Wang.pdf` — Page/cell refs for each extracted value
- MathCAD PDF: `digitalmodel/docs/modules/ship-design/passing_ship/Wang Paper calculations 3.pdf`
- VBA reference: `acma-projects/_engineering/passing_ship/Nick Version/modPassingShip.bas`

**Unit system for benchmark table**: Imperial (ft, slug/ft³, lbf) — matching source documents. Python tests convert to SI before calling calculator, then convert results back for comparison.

**Benchmark test cases** (extract from paper/MathCAD, add as parametrized tests):

| # | Case | L₁ (ft) | A₁ (ft²) | L₂ (ft) | A₂ (ft²) | U (ft/s) | η (ft) | ξ (ft) | h (ft) | Expected | Source |
|---|------|---------|----------|---------|----------|---------|--------|--------|--------|----------|--------|
| 1 | Infinite, sway, ξ=0 | 950 | 3192 | 475 | 6413 | 11.2 | 190 | 0 | ∞ | Sway ≈ 76,440 lbf | MathCAD p.X |
| 2 | Infinite, surge, ξ=0 | 950 | 3192 | 475 | 6413 | 11.2 | 190 | 0 | ∞ | Surge ≈ 0 (symmetry) | MathCAD p.X |
| 3 | Infinite, sway, ξ=+0.25L₁ | 950 | 3192 | 475 | 6413 | 11.2 | 190 | 237.5 | ∞ | Extract from MathCAD | TBD |
| 4 | Infinite, surge, ξ=+0.25L₁ | 950 | 3192 | 475 | 6413 | 11.2 | 190 | 237.5 | ∞ | Extract from MathCAD | TBD |
| 5 | Infinite, yaw, ξ=+0.25L₁ | 950 | 3192 | 475 | 6413 | 11.2 | 190 | 237.5 | ∞ | Extract from MathCAD | TBD |
| 6 | Infinite, sway, ξ=-0.5L₁ | 950 | 3192 | 475 | 6413 | 11.2 | 190 | -475 | ∞ | Extract from MathCAD | TBD |
| 7 | Finite, sway | 950 | 3192 | 475 | 6413 | 11.2 | 237.5 | 20 | 200 | Sway ≈ 52,550 lbf | MathCAD p.X |
| 8 | Finite, surge | 950 | 3192 | 475 | 6413 | 11.2 | 237.5 | 20 | 200 | Surge ≈ 1,929 lbf | MathCAD p.X |
| 9 | Finite, yaw | 950 | 3192 | 475 | 6413 | 11.2 | 237.5 | 20 | 200 | Extract from MathCAD | TBD |
| 10 | Velocity scaling | same | same | same | same | 22.4 | 190 | 0 | ∞ | ≈ 4× case 1 (U²) | Analytical |
| 11 | Separation sensitivity | same | same | same | same | 11.2 | 380 | 0 | ∞ | < case 1 | Analytical |
| 12 | Very shallow (h/T≈1.2) | same | same | same | same | 11.2 | 190 | 0 | 60 | Amplified vs ∞ | Analytical |
| 13 | Full stagger sweep | same | same | same | same | 11.2 | 190 | -L₁..+L₁ | ∞ | Force profile curve | VBA |

Note: "TBD" values to be extracted from MathCAD PDFs during Phase 1 execution. "p.X" = page reference to be filled in.

- [ ] Create `tests/hydrodynamics/passing_ship/test_wang_paper_benchmark.py`
- [ ] Extract numerical reference values from MathCAD PDFs (fill TBD cells above)
- [ ] Add exact source page/cell citations for each reference value
- [ ] Implement parametrized tests for cases 1-12
- [ ] Implement stagger sweep test (case 13): compare Python vs VBA at 21 positions (ξ = -L₁ to +L₁ in 0.1L₁ steps)
- [ ] Validate finite depth correction factor against VBA `Wang_Sway_Depth()` at depth ratios h/T = {1.2, 1.5, 2.0, 3.0, 5.0, 10.0, ∞}
- [ ] Generate benchmark comparison plot: Python vs VBA vs MathCAD
- [ ] Test edge cases: η → 0 (expect error/warning, not silent zero), h/T < 1.2 (expect warning)
- [ ] Document pass/fail with tolerances:
  - Infinite depth: 1% relative error (locked to `integration_tolerance=1e-4`, `scipy.integrate.dblquad`)
  - Finite depth: 5% relative error initially (existing implementation has "simplified" comment; tighten to 2% after formulation fix if needed)
- [ ] If finite depth exceeds 5%: flag as known gap, create follow-up task to refine `finite_depth_correction()` against Wang's exact series

**Deliverables**:
- Module consolidated at `hydrodynamics/passing_ship/`
- All tests passing at new location
- `test_wang_paper_benchmark.py` with reference data
- Benchmark report: Python vs Wang paper / VBA / MathCAD
- CLI functional with `--dry-run` mode

**Exit Criteria**: All tests pass, Wang paper benchmark cases within tolerance, old module removed.

---

### Phase 2: PassingShipSpec Schema + Force Time History

**Objective**: Create production-quality YAML-driven spec and generate force time histories.

**Tasks**:
- [ ] Design `PassingShipSpec` schema (see Schema Design below)
- [ ] Implement `from_yaml()` / `to_yaml()` with Pydantic v2
- [ ] Create `spec_template.yml` with all supported fields
- [ ] Implement `ForceTimeHistory` class:
  - Transit simulation: passing ship moves along track at constant velocity
  - Compute forces at each timestep as relative position changes
  - Output: time series of surge/sway/yaw forces on moored vessel
- [ ] Investigate perpendicular passing geometry support:
  - Wang formulation assumes parallel passing (no angle parameter in kernel functions)
  - Perpendicular/oblique may require coordinate rotation of the transit track, NOT a new force model
  - If rotation approach is insufficient, flag as formulation gap and document limitations
  - Minimum: parallel passing is fully supported; oblique is best-effort with documented assumptions
- [ ] Add wind force combination (optional per spec):
  - Clarify method: Python calculates wind forces directly (e.g., OCIMF coefficients) and adds to time history
  - OR: wind is configured in OrcaFlex model environment for solver to handle (Phase 3)
  - Avoid double-counting — document which approach and why
- [ ] Write unit tests for schema validation and time history generation
- [ ] Write integration test: spec.yml → force time history → CSV export

**Schema Design (PassingShipSpec)**:
```yaml
version: "1.0"
analysis_type: passing_ship

moored_vessel:
  name: "Moored_Tanker"
  length_bp: 274.0          # m
  beam: 48.0                # m
  draft: 16.0               # m
  block_coefficient: 0.85
  midship_area: null         # auto-calculated if null
  mooring:                   # optional — triggers mooring response
    orcaflex_model: "mooring_model.dat"
    line_names: ["Line1", "Line2", ...]

passing_vessel:
  name: "Container_Ship"
  length_bp: 300.0
  beam: 45.0
  draft: 14.0
  block_coefficient: 0.70
  midship_area: null

environment:
  water_depth: 25.0          # m (or "infinite")
  water_density: 1025.0      # kg/m³
  current_velocity: 0.0      # m/s (ambient)
  wind:                       # optional
    speed: 15.0               # m/s
    direction: 90.0           # degrees from north

passing_scenario:
  velocity: 6.0               # m/s (passing ship speed)
  lateral_separation: 100.0   # m (centerline to centerline)
  passing_angle: 0.0          # 0=parallel, 90=perpendicular
  stagger_range:               # longitudinal range for time history
    start: -500.0              # m (before abeam)
    end: 500.0                 # m (after abeam)
  time_step: 0.5              # s

solver_options:
  integration_tolerance: 1.0e-4
  finite_depth_terms: 10
  cache_enabled: true

outputs:
  format: [csv, html]
  directory: "results/"
  include_plots: true

metadata:
  project: ""
  description: ""
  author: ""
```

**Deliverables**:
- `PassingShipSpec` Pydantic model with full validation
- `ForceTimeHistory` generator producing time series
- Example `spec_template.yml`
- Unit + integration tests

**Exit Criteria**: `spec.yml` → force time history → CSV/plot pipeline works end-to-end.

---

### Phase 3: Mooring Response Integration

**Objective**: Apply passing ship forces to OrcaFlex mooring models and extract response.

#### Force-to-OrcaFlex Load Mapping Contract

The Wang calculator outputs forces in the Wang coordinate system. These must be mapped to OrcaFlex applied loads with explicit transforms:

| Wang Output | OrcaFlex Applied Load | Transform |
|-------------|----------------------|-----------|
| Surge force (F_x) | Vessel global Fx | Sign check: Wang +x = OrcaFlex +x (fwd) |
| Sway force (F_y) | Vessel global Fy | Sign check: Wang +y may differ from OrcaFlex +y |
| Yaw moment (M_z) | Vessel global Mz | Sign check: Wang CW vs OrcaFlex CW |

- Reference point: Forces applied at moored vessel centre of gravity
- Application method: `OrcFxAPI.ExternalFunction` or pre-computed `TimeHistory` data object
- Time base: Wang transit time history → OrcaFlex simulation period with ramp-up/ramp-down

**Tasks**:
- [ ] Document coordinate transform between Wang → OrcaFlex (sign test with known case)
- [ ] Implement `MooringResponse` class:
  - Load OrcaFlex model (`.dat` or `.yml`)
  - Apply force time history as external loads on moored vessel via `TimeHistory` data
  - Run OrcaFlex time-domain simulation
  - Extract: line tensions, vessel motions (6 DOF), fender loads
- [ ] Define `MooringResponseResults` output schema:
  - Peak/max tensions per line
  - Max vessel excursions (surge, sway, yaw)
  - Fender compression (if applicable)
  - Time series of key responses
- [ ] Handle cases where OrcaFlex is not available (dry-run mode)
- [ ] Write tests with mock OrcaFlex model (fixture `.yml`)

**Deliverables**:
- `MooringResponse` class with OrcaFlex integration
- `MooringResponseResults` output schema
- Dry-run mode for CI without OrcaFlex license
- Tests with fixture model

**Exit Criteria**: Force time history → OrcaFlex run → mooring tensions extracted.

---

### Phase 4: Parametric Study Engine

**Objective**: Generate and execute case matrices covering multiple passing scenarios.

**Tasks**:
- [ ] Implement `ParametricEngine` class:
  - Define case matrix dimensions: velocity, separation, passing angle, wind conditions
  - Generate all combinations from spec ranges
  - Execute in parallel (ThreadPoolExecutor)
  - Aggregate results into envelope summaries
- [ ] Support case filtering (skip impossible combinations)
- [ ] Results aggregation:
  - Governing case identification (which combination gives max tension/motion)
  - Envelope plots across parameters
  - Summary table of all cases
- [ ] Write tests for matrix generation and aggregation

**Deliverables**:
- `ParametricEngine` with parallel batch execution
- Case matrix YAML definition format
- Envelope extraction and governing case identification
- Tests

**Exit Criteria**: Multi-case parametric study completes, governing case identified.

---

### Phase 5: Benchmark Validation

**Objective**: Validate against 5-7 historical projects from archive.

**Tasks**:
- [ ] Survey `acma-projects/` for suitable benchmark cases
- [ ] For each case:
  - Create sanitized `spec.yml` (no client identifiers — legal compliance)
  - Run through pipeline
  - Compare against archived project results
  - Document tolerance: tensions within 5%, motions within 10%
- [ ] Legal sanity scan on all benchmark files
- [ ] Benchmark report: pass/fail per case with deviation metrics

**Candidate Projects** (to be confirmed after archive survey):
- B1512 (has MathCAD reference data)
- Additional projects from `R:\Archive - Drive J\` (if accessible)

**Deliverables**:
- 5-7 sanitized `spec.yml` benchmark cases
- Benchmark comparison report
- All cases within tolerance or documented exceptions

**Exit Criteria**: Minimum 5 benchmark cases pass within tolerance.

---

### Phase 6: HTML Report Generation

**Objective**: Standardized reporting with interactive plots.

**Tasks**:
- [ ] Create Jinja2 HTML report template
- [ ] Report sections:
  - Executive summary (vessel details, scenario, governing results)
  - Force time history plots (surge/sway/yaw vs time)
  - Mooring response plots (tension time histories, vessel motion)
  - Parametric study results (envelope plots, governing case table)
  - Input summary (spec.yml echo)
- [ ] Use Plotly for interactive charts
- [ ] Follow WRK-129/WRK-130 reporting patterns when available
- [ ] Write tests for report generation

**Deliverables**:
- HTML report template
- `ReportGenerator` class
- Example report from benchmark case
- Tests

**Exit Criteria**: HTML report generates from any completed analysis.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| VBA/Python formulation mismatch | Low | High | Phase 1c cross-validation with 13 benchmark cases before building further |
| Unit system confusion (Imperial reference vs SI code) | Medium | High | Phase 1c: explicit unit documentation, dual-unit test cases, conversion at boundaries |
| Coordinate/sign convention mismatch | Medium | High | Phase 1c: sign convention table, verified against known case before Phase 3 |
| Finite depth correction inaccurate | Medium | Medium | Phase 1d: validate against MathCAD finite-depth variant (not deep water); 5% tolerance initially, tighten after formulation fix |
| Perpendicular passing is a formulation gap | Medium | Medium | Phase 2: investigate coordinate rotation approach; document limitations if not fully solvable |
| OrcaFlex license unavailable in CI | Medium | Medium | Dry-run mode, mock fixtures, CI gate split (with/without OrcaFlex) |
| Migration breakage (old import paths) | Low | Medium | Phase 1a: staged migration with compatibility shim, scan all consumers |
| Archive projects inaccessible (R: drive) | Medium | Medium | Use local cases from `acma-projects/`; reduce benchmark count if needed |
| Legal compliance violations in benchmark data | Medium | High | Legal scan on every benchmark file; sanitize before commit; verify "B1512" against deny list |
| Numerical instability at small separations | Low | Medium | Phase 1d: edge case tests at η→0; guard with error/warning |
| Large scope — incomplete delivery | Medium | Medium | Phases are independent; partial delivery is useful |

---

## Dependencies

| Dependency | Required By | Status |
|------------|-------------|--------|
| Existing `python_code_passing_ship/` module | Phase 1 | Available |
| VBA reference (`modPassingShip.bas`) | Phase 1 | Available |
| `DiffractionSpec` pattern (for schema design) | Phase 2 | Available |
| OrcaFlex / OrcFxAPI | Phase 3 | Available (license-gated) |
| Archive projects for benchmarking | Phase 5 | Partially available (B1512 confirmed) |
| WRK-129/WRK-130 reporting framework | Phase 6 | Pending (can proceed independently) |

---

## Cross-Review Process (MANDATORY)

### Review Status

| Gate | Status | Requirement |
|------|--------|-------------|
| Review Iterations | 1/3 | Minimum 3 iterations |
| Codex Approved | Changes Requested | Hard gate |
| Gemini Approved | Approved | Soft gate |
| Legal Scan | Pending | Must pass |

### Review Iteration Log

| Iter | Date | Reviewer | Verdict | Findings | Fixed |
|------|------|----------|---------|----------|-------|
| 1 | 2026-02-15 | Claude | MINOR | 14: sign conventions, unit traps, thin benchmarks, ghost import, edge cases, legal paths, solver conflict, perpendicular gap, water_depth type, OrcaFlex mapping | 14/14 addressed in spec v1.1 |
| 1 | 2026-02-15 | Codex | MAJOR | 7: no migration shim, benchmark under-specified, tolerance untied to settings, finite-depth mitigation wrong, missing load mapping, incomplete risks, test robustness | 7/7 addressed in spec v1.1 |
| 1 | 2026-02-15 | Gemini | APPROVE | 1: wind integration method unclear (direct calc vs OrcaFlex env) | 1/1 addressed in spec v1.1 |
| 1 | — | Codex | — | — | — |
| 1 | — | Gemini | — | — | — |
| 2 | — | Codex | — | — | — |
| 2 | — | Gemini | — | — | — |
| 3 | — | Codex | — | — | — |
| 3 | — | Gemini | — | — | — |

---

## Acceptance Criteria (from WRK-131)

- [ ] PassingShipSpec Pydantic schema defined and validated
- [ ] Force calculation implemented from existing code (stabilized)
- [ ] Force time history generation for passing scenarios
- [ ] Mooring response analysis with line tensions and motions
- [ ] Parametric study capability
- [ ] 5-7 benchmark cases reproduced within tolerance (tension 5%, motions 10%)
- [ ] Sanitized spec.yml files for each benchmark
- [ ] Standardized HTML reports with force plots and tension envelopes

---

## Progress Tracking

| Milestone | Target | Status |
|-----------|--------|--------|
| Phase 1: Stabilize existing code | — | Pending |
| Phase 2: Schema + time history | — | Pending |
| Phase 3: Mooring response | — | Pending |
| Phase 4: Parametric engine | — | Pending |
| Phase 5: Benchmark validation | — | Pending |
| Phase 6: HTML reports | — | Pending |

---

## Appendix

### A. Related Work Items

| ID | Title | Relationship |
|----|-------|-------------|
| WRK-039 | SPM project benchmarking (AQWA vs OrcaFlex) | Mooring analysis patterns |
| WRK-125 | OrcaFlex module roadmap | Coordination |
| WRK-129 | Standardize OrcaFlex reporting | Report template patterns |
| WRK-130 | Standardize OrcaWave reporting | Report template patterns |

### B. Reference Materials

| Document | Location |
|----------|----------|
| Wang formulations (VBA) | `acma-projects/_engineering/passing_ship/Nick Version/modPassingShip.bas` |
| Quadrature engine (VBA) | `acma-projects/_engineering/passing_ship/Nick Version/modQuadrature.bas` |
| PassingShipForces.pdf | `acma-projects/_engineering/passing_ship/Nick Version/PassingShipForces.pdf` |
| MathCAD: Deep water | `acma-projects/B1512/data/passing_ship/PassShip FandM Deep.xmcd` |
| MathCAD: Wang calcs | `acma-projects/B1512/data/passing_ship/Calculation of forces and moments from Wang.xmcd` |
| AQWA tutorial | `acma-projects/_aqwa/passing_ship_tutorial.pdf` |
| DiffractionSpec pattern | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py` |

### C. Change History

| Date | Version | Change |
|------|---------|--------|
| 2026-02-15 | 1.0 | Initial spec created |
| 2026-02-15 | 1.1 | Cross-review fixes: staged migration, Wang benchmark expanded to 13 cases, sign/unit conventions section, finite-depth tolerance relaxed to 5%, perpendicular passing flagged as formulation gap, OrcaFlex load mapping contract, expanded risk assessment |
