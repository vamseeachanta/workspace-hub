---
title: "Fitness-for-Service Module Roadmap: Wall Thickness Grid, Industry Targeting, Asset Lifecycle"
description: "Enhance pyintegrity FFS module with UT grid-based Level 1/2 acceptance workflow, industry-specific parameter sets, and asset lifecycle remaining-life integration"
version: "1.0"
module: "digitalmodel/asset_integrity"
session:
  id: ""
  agent: "claude-opus-4-6"
  started: "2026-02-13"
  last_active: "2026-02-13"
  conversation_id: ""
review:
  required_iterations: 3
  current_iteration: 1
  status: "in_progress"
  reviewers:
    openai_codex:
      status: "changes_requested"
      iteration: 1
    google_gemini:
      status: "changes_requested"
      iteration: 1
    legal_sanity:
      status: "pending"
      iteration: 0
      violations: 0
status: "approved"
progress: 0
phase: 0
blocked_by: []
created: "2026-02-13"
updated: "2026-02-13-r2"
priority: "medium"
complexity: "high"
risk: "medium"
tags: [ffs, api-579, wall-thickness, pyintegrity, lifecycle, corrosion, inspection]
links:
  spec: ".claude/work-queue/pending/WRK-138.md"
  issues: ["WRK-138"]
  docs:
    - "digitalmodel/reports/modules/marketing/marketing_brochure_api579_ffs.md"
history:
  - date: "2026-02-13"
    action: "created"
    by: "claude-opus-4-6"
    notes: "Initial roadmap from deep module exploration + industry research"
  - date: "2026-02-13"
    action: "cross-reviewed"
    by: "claude-opus-4-6, codex-cli, gemini-cli"
    notes: "R1: Claude MINOR (14), Codex MAJOR (10), Gemini MINOR (4 categories). All findings addressed."
  - date: "2026-02-13"
    action: "approved"
    by: "user"
    notes: "Plan approved. Module renamed to asset_integrity. Reference data formats added from 3 historical projects + energy_integrity (20+ campaigns)."
---

# Fitness-for-Service Module Roadmap

> **Module**: `digitalmodel/asset_integrity` (renamed from `data_systems/pyintegrity`) | **Status**: Draft | **Priority**: Medium
> **Work Item**: WRK-138 | **Related**: WRK-044 (pipeline wall thickness — complementary)

## Executive Summary

The `pyintegrity` module has a solid foundation for FFS assessments — API 579 Parts 4 and 5 (metal loss, Level 1/2) plus BS 7910 fracture mechanics (crack-like flaws via FAD). However, the gap between marketed capabilities and actual implementation is significant — only 2 of 13 API 579 parts are implemented (plus BS 7910 as a parallel standard), the example file doesn't exist, there are only ~4 effective tests (some are shams), and the module serves pipelines exclusively.

This roadmap addresses 4 user-requested enhancements:
1. **Wall thickness grid workflow** — accept UT inspection grids, produce Level 1/2 accept/reject results
2. **Working examples** — catalog what exists, fix what's broken, add industry-specific examples
3. **Industry targeting** — extend beyond pipelines to upstream vessels, midstream, and downstream refinery equipment
4. **Asset lifecycle** — corrosion trending, remaining life, inspection intervals, degradation tracking

The approach builds on the existing codebase (8,700 LOC, YAML-driven, grid processing already exists) rather than rewriting.

---

## Current State Assessment

### What Works (Keep)

| Capability | Implementation | Quality |
|-----------|---------------|---------|
| Part 4 GML Level 1/2 | `API579_components.py` (997 lines) | Production-ready for pipes |
| Part 5 LML Level 1/2 | Same file, RSF + Folias factor | Production-ready for pipes |
| BS 7910 Crack-Like Flaws | `BS7910_critical_flaw_limits.py` (1,221 lines) | Comprehensive FAD (Note: this is BS 7910, not API 579 Part 9) |
| Excel grid input | `data.py` ReadingSets from .xlsx | Works, needs format expansion |
| Remaining life (basic) | Single-point linear extrapolation: `(tam - tmin) / rate` | Functional but simplistic, needs multi-point trending |
| YAML config system | `engine.py` → `ApplicationManager` | Well-structured, extensible |
| Visualization | `visualizations.py` (729 lines) contour/heatmap | Good, needs report integration |
| B31G pipeline assessment | `PipeCapacity.py` (860 lines) | B31.4, B31.8, API RP 1111 |

### What's Missing (Build)

| Gap | Impact | Priority |
|-----|--------|----------|
| Accept/reject decision output | User can't get pass/fail verdict directly | P0 |
| Working examples | `basic_usage.py` is empty placeholder | P0 |
| CSV/JSON grid input | Excel-only limits integration | P1 |
| Industry-specific workflows | Pipeline-only, no vessels/tanks | P1 |
| Multi-point corrosion trending | Single snapshot only, no regression | P1 |
| Inspection interval logic | No API 510/570/653 alignment | P2 |
| Part 6 pitting assessment | Common mechanism, not implemented | P2 |
| Part 12 dents & gouges | High pipeline demand | P2 |
| Part 7 HIC/SOHIC | Critical for refineries | P3 |
| Level 3 FEA hooks | No integration path | P3 |
| Test coverage | ~4 effective tests (6 functions, 2 are shams comparing empty dicts), need 80+ | P0 |

### Marketing vs Reality

The brochure (`marketing_brochure_api579_ffs.md`, 492 lines) claims:
- "All 13 assessment parts" → **Actually 2 API 579 parts (4, 5) + BS 7910** (fracture mechanics, separate standard)
- "200+ steel grades" → **Actually 0 in code** (`MaterialProperties.get_material_properties()` is `pass`; properties are manually entered per YAML config)
- "150+ verification tests" → **Actually ~4 effective tests** (some BS 7910 tests compare empty dicts)
- "12+ corrosion mechanisms" → **Actually 1** (uniform rate extrapolation)
- "15+ component types" → **Actually 1** (cylindrical pipe)
- **B31G method has broken import path** — `b31g()` references `results.API579.customInputs` (should be `pyintegrity.custom.API579.customInputs`)

**Action**: The brochure must be corrected to reflect actual capabilities after each roadmap phase. Overclaiming creates liability risk.

---

## Reference Data Formats (from Historical Projects)

Three reference project directories plus `energy_integrity/` (15+ sub-projects, 20+ inspection campaigns) were analyzed. The following data formats and patterns must be supported.

### Wall Thickness Grid Formats

| Format | Convention | Example | Handling |
|--------|-----------|---------|----------|
| **C-scan percentage** | 80-120% of nominal from vendor tool | `K2 West_rev1.xlsx` (C-scans sheets) | Multiply by `DataCorrectionFactor` (typically 0.833) to get absolute |
| **Absolute thickness** | Direct inches from UT probe | `Gas export area 1 grid_UT.xlsx` | Use directly |
| **Simple indexed grid** | Integer row/col indices (0,1,2...) | `K2_P14_SignalFFS_Benchmark.xlsx` | Map to physical coords via spacing |
| **Physical coordinate grid** | Row/col headers in inches or degrees | `talos_10_in_cml28.xlsx` (1.5" spacing) | Use directly as spatial reference |

### C-Scan Sheet Structure (Vendor Format)

```
Rows 0-34:  Metadata (scan zone, probe, footprint, pulse params)
Row 35:     X-axis angular coordinates (degrees): 40, 43.68, 47.37...
Row 36:     Empty separator
Row 37:     Y-axis linear coordinates (inches): 0.0, 2.26, 4.52...
Rows 38+:   Data grid — percentage of nominal wall thickness
```

Grid parser must handle: `skiprows` (to bypass metadata), `skipfooter`, `DataCorrectionFactor`, NaN for unmeasured locations.

### Established YAML Config Pattern

All historical projects use a consistent YAML structure that must be preserved:

```yaml
ReadingSets:
  - io: path/to/grid.xlsx        # Grid file reference
    sheet_name: Sheet1
    index_col: 0
    skiprows: 0                   # Skip vendor metadata headers
    DataCorrectionFactor: 1.00    # 0.833 for percentage C-scans
    Label: "area_1"
    FCARate: "Historical"         # or explicit float (in/yr)
    FCA: [0.00, 0.02, 0.04, 0.06]  # FCA scenario array

LML:
  LTA:
    - io: path/to/grid.xlsx
      sIndex: [4, 8]             # Axial extent (row indices)
      cIndex: [4, 8]             # Circumferential extent (col indices)
      Lmsd: 1.45                 # Measured defect dimension (inches)
      MtType: "Cylindrical"
      FCA: [0.00, 0.02, 0.04]
```

### Multi-Run Inspection Data

Historical projects contain multiple inspection campaigns on the same assets:

| Evidence | Pattern | Use for Trending |
|----------|---------|-----------------|
| Revision files | `K2 West_rev1.xlsx`, `K2 West_rev2.xlsx` | Compare grids at different dates |
| Date-stamped folders | `2018-11-01/`, `2019-07-11/` | Extract inspection dates |
| Multiple CMLs | `cml28`, `cml31` on same pipe | Spatial corrosion distribution |
| Historical rates in YAML | `FCARate: 0.0143` (in/yr) | Validate computed rates |
| Multiple methods | PEC + UT on same pipe sections | Cross-method validation |

Phase 3 (lifecycle trending) must accept a list of `(date, grid_file)` pairs for the same component to compute multi-point corrosion rates.

### Reference Projects (Sanitized — No Client Names in Code)

| ID | Content | FFS Relevance | Multi-Run |
|----|---------|--------------|-----------|
| Ref A | GML + LML analysis, C-scan grids, YAML configs | High — full FFS workflow | rev1/rev2 |
| Ref B | LML analysis, 13x14 grids, CML28/31 | High — LML with sIndex/cIndex | CML points |
| Ref C | B31.4/B31.8 tmin design verification | Low — design, not FFS | N/A |
| energy_integrity | 15+ FFS sub-projects | **Highest** — 20+ campaigns | Date-stamped |

---

## Roadmap Phases

### Phase 0: Examples & Audit (Pre-Implementation)

**Objective**: Catalog what works, fix what's broken, create working examples before any new code.

**Rationale**: The user explicitly requested "add existing examples prior to proceeding." This phase validates the foundation.

**Tasks**:
- [ ] 0.1: Audit all 3 test YAML configs — run each, document pass/fail/error
- [ ] 0.2: Audit `PipeCapacity.py` code references — verify B31.4/B31.8 equation numbers
- [ ] 0.3: **Fix B31G broken import path** — `b31g()` method at line 398 of `API579_components.py` references wrong module
- [ ] 0.4: **Legal compliance scan** — check test YAML files for client-identifying text (e.g. "Client Asset" in `16in_gas_b318.yml`), sanitize per `.claude/rules/legal-compliance.md`
- [ ] 0.5: **Fix sham tests** — BS 7910 tests that compare empty dicts, remove `sys.argv` manipulation, remove direct function calls at module level
- [ ] 0.6: Create `examples/ffs/` directory with 3 working examples:
  - `example_gml_16in_gas_pipeline.py` — Part 4 GML from existing test data
  - `example_lml_12in_oil_pipeline.py` — Part 5 LML from existing test data
  - `example_bs7910_crack_assessment.py` — BS 7910 fracture from existing test data
- [ ] 0.7: Each example must: load config, run assessment, print accept/reject, save report
- [ ] 0.8: Write 15+ unit tests for existing GML/LML/B31G calculations with known benchmark values
- [ ] 0.9: Create `basic_usage.py` with working quickstart (file does not currently exist)
- [ ] 0.10: **Rename module** `data_systems/pyintegrity` → `asset_integrity` (top-level under digitalmodel)
  - Move `src/digitalmodel/data_systems/pyintegrity/` → `src/digitalmodel/asset_integrity/`
  - Update all 102 internal references across 31 files
  - Add compat shim: `data_systems.pyintegrity` → `asset_integrity` with DeprecationWarning
  - Update imports in tests, configs, and docs
- [ ] 0.11: Correct marketing brochure to reflect actual current capabilities

**Deliverables**:
- 3 working example scripts with sample output
- Audit report documenting actual vs claimed capabilities
- 15+ new tests (target: existing code at 80% coverage)
- Corrected brochure (what's real today, roadmap items marked as "planned")

**Exit Criteria**:
- [ ] All 3 examples run end-to-end and produce accept/reject output
- [ ] All existing + new tests pass
- [ ] Brochure matches reality

---

### Phase 1: Wall Thickness Grid Accept/Reject Workflow

**Objective**: Engineer gives a wall thickness grid → gets Level 1 and Level 2 accept/reject verdict.

This is the core user request and the highest-value enhancement.

**Architecture**:

```
Input (CSV/XLSX/YAML grid)
    │
    ▼
┌─────────────────────┐
│  Grid Parser        │  ← Normalize any input format to 2D array
│  (grid_parser.py)   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Assessment Router  │  ← Auto-detect: GML (Part 4) vs LML (Part 5)
│  (ffs_router.py)    │     Based on API 579 assessment length (L_a) applicability criteria
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌────────┐ ┌────────┐
│Level 1 │ │Level 2 │  ← Both always run; L2 only if L1 fails
│Screener│ │Engine  │
└────┬───┘ └────┬───┘
     │          │
     ▼          ▼
┌─────────────────────┐
│  Decision Engine    │  ← Accept / Reject / Monitor / Repair
│  (ffs_decision.py)  │     Per API 579 Parts 4/5 assessment flowcharts
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Report Generator   │  ← Grid heatmap + verdict table + remaining life
│  (ffs_report.py)    │
└─────────────────────┘
```

**Tasks**:
- [ ] 1.1: `grid_parser.py` — Unified grid input (CSV, XLSX, YAML array, NumPy)
  - Normalize to `pd.DataFrame` with row=longitudinal, col=circumferential
  - Handle **two value conventions**: percentage of nominal (C-scan vendor format, apply `DataCorrectionFactor`) and absolute thickness (UT direct)
  - Handle **two coordinate systems**: physical coordinates (inches/degrees) and simple integer indices
  - Handle **C-scan metadata headers**: use `skiprows`/`skipfooter` to bypass vendor probe/pulse metadata (rows 0-34 typical)
  - Handle NaN for unmeasured locations (interpolate or flag)
  - Validate dimensions against component geometry
  - Support CML point data (irregular spacing) with interpolation to grid
  - **Unit conversion**: accept both inches and mm input, normalize internally
- [ ] 1.2: `ffs_router.py` — Auto-classify damage type per API 579 definitions
  - GML (Part 4): wall loss extends over assessment length L_a (per Part 4, Section 4.3.3 applicability)
  - LML (Part 5): wall loss is localized — flaw dimensions (s, c) relative to component geometry (per Part 5, Section 5.3.3)
  - User override: force specific part
  - Note: Part 6 (pitting) is out of scope for this roadmap — router returns "Part 6 not implemented" stub if pit-like morphology detected
- [ ] 1.3: `level1_screener.py` — Level 1 screening
  - Calculate t_min per applicable code (ASME VIII Div 1/2, B31.4, B31.8)
  - Compare t_mm (minimum measured) to t_min
  - **Output**: `ACCEPT` if t_mm >= t_min, else `FAIL_LEVEL_1`
- [ ] 1.4: `level2_engine.py` — Level 2 detailed assessment
  - For GML: area-averaged thickness (t_am) vs assessment length
  - For LML: RSF calculation with Folias factor
  - MAWP at current condition vs operating pressure
  - **Output**: `ACCEPT` if RSF >= RSF_a (0.9 default), else `FAIL_LEVEL_2`
- [ ] 1.5: `ffs_decision.py` — Decision engine
  - Accept: continue service, set next inspection interval
  - Monitor: increase inspection frequency
  - Repair: recommend per ASME PCC-2
  - Re-rate: reduce MAWP to current capability
  - Replace: remaining life exhausted
- [ ] 1.6: `ffs_report.py` — Report generator
  - Grid heatmap with accept/reject coloring per cell
  - Summary table: t_min, t_mm, t_am, RSF, MAWP, verdict
  - Governing location identification
  - Export: HTML, CSV, YAML results

**New Files** (under `src/digitalmodel/asset_integrity/`):
```
assessment/
  __init__.py
  grid_parser.py       (~200 lines — CSV/XLSX/YAML + CML interpolation)
  ffs_router.py        (~100 lines — Part 4/5 applicability + stub for Part 6)
  level1_screener.py   (~150 lines — t_min per code + component-specific rules)
  level2_engine.py     (~300 lines — GML area averaging + LML RSF + flaw interaction)
  ffs_decision.py      (~120 lines — decision outcomes + disclaimers for near-limit cases)
  ffs_report.py        (~200 lines — heatmap + summary + assumptions/limitations)
```

**Tests**: 25+ tests
- Grid parsing: CSV, XLSX, YAML, irregular CML points
- Level 1 screening: pass case, fail case, boundary case
- Level 2 RSF: known benchmark (API 579 Part 5 Example Problem)
- Decision logic: each outcome path
- Report generation: verify output format

**Deliverables**:
- Working accept/reject pipeline from grid input to verdict
- 2 new examples: `example_grid_level1_level2.py`, `example_csv_grid_assessment.py`

**Exit Criteria**:
- [ ] Grid → Level 1 → Level 2 → Verdict pipeline works end-to-end
- [ ] At least one API 579 benchmark case verified numerically
- [ ] 25+ tests passing

---

### Phase 2: Industry-Specific Parameter Sets

**Objective**: Support pipelines, upstream vessels, midstream piping, and downstream refinery equipment with appropriate design codes and default parameters.

**Architecture**:

```yaml
# Industry presets loaded from YAML
industry_presets/
  upstream.yml      # Wellhead, separators, flowlines
  midstream.yml     # Transmission pipelines, compressor stations
  downstream.yml    # Refinery vessels, heat exchangers, towers
  common.yml        # Shared material database, safety factors
```

**Tasks**:
- [ ] 2.1: `industry_presets/` — YAML parameter sets per industry
  - **Upstream**: CO2/H2S corrosion rates, separator vessels, ASME VIII Div 1/2
  - **Midstream**: Pipeline B31.4/B31.8 (exists), add compressor station vessels, metering
  - **Downstream**: Sulfidation rates, naphthenic acid, ASME VIII, high-temperature materials
- [ ] 2.2: `material_database.py` — Expand from ~10 to 50+ common steel grades
  - Pipeline: X42, X46, X52, X56, X60, X65, X70, X80
  - Vessel: SA-516 Gr 55/60/65/70, SA-387 Gr 11/22, SA-240 (stainless)
  - High-temp: SA-335 P11/P22/P91
  - Properties: SMYS, SMTS, allowable stress vs temperature, E, Poisson's ratio
- [ ] 2.3: `component_types.py` — Extend beyond cylindrical pipes
  - Cylindrical shell (exists)
  - Spherical head/vessel
  - Ellipsoidal head (2:1)
  - Conical section
  - Flat plate (tank floor)
  - Nozzle/branch connection (simplified)
- [ ] 2.4: `design_codes.py` — t_min calculation per applicable code
  - ASME Section VIII Div 1 (vessels) — UG-27, UG-32, UG-33
  - ASME Section VIII Div 2 (alternative rules)
  - ASME B31.4 (liquid pipelines) — exists, verify
  - ASME B31.8 (gas pipelines) — exists, verify
  - ASME B31.3 (process piping)
  - DNV-RP-F101 (corroded pipeline — alternative to B31G)
- [ ] 2.5: Integrate presets into YAML config system
  - `preset: midstream/transmission_pipeline` loads defaults
  - User overrides any preset value
  - Preset validation: warn if operating conditions outside preset range
- [ ] 2.6: Add 3 industry-specific examples:
  - `example_upstream_separator.py` — 48" separator, SA-516 Gr 70
  - `example_midstream_pipeline.py` — 20" gas transmission, X65
  - `example_downstream_tower.py` — distillation column shell, SA-516 Gr 60

**New Files**:
```
industry/
  __init__.py
  presets.py            (~120 lines - preset loader + validation)
  material_database.py  (~400 lines - 50+ grades with temp-dependent properties)
  component_types.py    (~300 lines - 6 geometry types with stress formulas)
  design_codes.py       (~350 lines - 4+ codes with clause-traceable equations)
industry_presets/
  upstream.yml          (~80 lines)
  midstream.yml         (~80 lines)
  downstream.yml        (~80 lines)
  common.yml            (~120 lines - materials, safety factors)
```

**Tests**: 20+ tests
- Each component type: t_min calculation vs hand calc
- Each design code: at least one benchmark
- Preset loading and override behavior
- Material database: all grades have required properties

**Exit Criteria**:
- [ ] 3 industry presets with appropriate defaults
- [ ] 50+ material grades with properties
- [ ] 5+ component types supported in t_min calculation
- [ ] 4+ design codes for t_min
- [ ] 20+ tests passing

---

### Phase 3: Asset Lifecycle Integration

**Objective**: Track degradation over time, predict remaining life, recommend inspection intervals.

**Architecture**:

```
Inspection History (multiple snapshots)
    │
    ▼
┌─────────────────────┐
│  Corrosion Trending  │  ← Linear, exponential, piecewise regression
│  (trending.py)       │     Multi-point CML history
└─────────┬────────────┘
          │
          ▼
┌─────────────────────┐
│  Remaining Life      │  ← Time to t_min at current rate
│  (remaining_life.py) │     Confidence intervals (68%, 95%)
└─────────┬────────────┘
          │
          ▼
┌─────────────────────┐
│  Inspection Planner  │  ← Next inspection per API 510/570/653
│  (inspection.py)     │     Half remaining life or code maximum
└─────────────────────┘
```

**Tasks**:
- [ ] 3.1: `trending.py` — Multi-point corrosion rate analysis
  - Input: list of `(date, grid_file)` pairs for the same component (multi-campaign)
  - Also accept: list of `(date, thickness)` pairs per CML point
  - Support historical rate discovery from revision files (rev1/rev2) and date-stamped folders
  - Validate computed rate against `FCARate` values in YAML configs where available
  - Linear regression: constant corrosion rate
  - Exponential regression: accelerating corrosion
  - Piecewise: detect rate change points
  - Output: current rate (in/yr or mm/yr), confidence interval, R-squared
  - Short-term vs long-term rate comparison
- [ ] 3.2: `remaining_life.py` — Enhanced remaining life calculation
  - Time to reach t_min at current corrosion rate
  - Time to reach t_min at upper confidence bound (conservative)
  - Sensitivity: remaining life vs assumed rate (parametric)
  - Account for FCA (future corrosion allowance)
  - Output: years remaining (best estimate, conservative, optimistic)
- [ ] 3.3: `inspection.py` — Inspection interval planner
  - API 510 rules: max interval, half remaining life
  - API 570 rules: piping inspection intervals
  - API 653 rules: tank inspection intervals
  - Risk factor adjustment: corrosion rate severity, consequence category
  - Output: next inspection date, recommended method (UT, RT, visual)
- [ ] 3.4: `lifecycle_report.py` — Lifecycle summary report
  - Timeline: design life → current age → remaining life → end of life
  - Corrosion rate trend plot with projection
  - Inspection history table
  - Decision recommendation: continue / increase monitoring / plan repair / plan replacement
- [ ] 3.5: Add lifecycle example:
  - `example_lifecycle_vessel.py` — 15-year separator with 5 inspection snapshots

**New Files**:
```
lifecycle/
  __init__.py
  trending.py          (~280 lines — linear/exp/piecewise regression + confidence intervals)
  remaining_life.py    (~180 lines — multi-scenario projection + sensitivity)
  inspection.py        (~200 lines — API 510/570/653 rules + risk adjustment)
  lifecycle_report.py  (~200 lines — timeline + trend plot + recommendations)
```

**Tests**: 20+ tests
- Trending: known rate recovery from synthetic data
- Remaining life: hand-calculated benchmarks
- Inspection intervals: API 510 Table 6.1 verification
- Edge cases: zero corrosion rate, accelerating corrosion, single data point

**Exit Criteria**:
- [ ] Multi-point corrosion trending with regression
- [ ] Remaining life with confidence intervals
- [ ] Inspection interval per API 510/570/653
- [ ] Lifecycle report generation
- [ ] 20+ tests passing

---

### Phase 4: Integration & Polish

**Objective**: Tie all phases together, update documentation, ensure end-to-end workflows.

**Tasks**:
- [ ] 4.1: End-to-end workflow integration
  - Grid input → Assessment → Remaining life → Inspection interval → Report
  - Single YAML config drives the entire pipeline
- [ ] 4.2: Update marketing brochure to reflect new capabilities accurately
- [ ] 4.3: Update `__init__.py` exports for clean public API
- [ ] 4.4: Add CLI entry point: `python -m pyintegrity --config assessment.yml`
- [ ] 4.5: Comprehensive example set (total 8-10 examples)
- [ ] 4.6: Full test suite target: 80+ tests, 80% coverage

**Exit Criteria**:
- [ ] 8+ working examples covering all industries and workflows
- [ ] 80+ tests, 80% coverage
- [ ] Brochure reflects reality
- [ ] WRK-138 acceptance criteria all met

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| API 579 equation errors | Medium | High | Verify against published worked examples and hand calcs |
| Marketing brochure liability | High | Medium | Correct brochure in Phase 0 before any external exposure |
| Scope creep to all 13 parts | Medium | Medium | Roadmap explicitly limits to Parts 4, 5; other parts are future WRK items |
| Existing code regressions | Medium | Medium | Phase 0 audit + test baseline before changes |
| Material database accuracy | Low | High | Source all properties from published standards (ASME II Part D) |
| Config format changes | Low | Medium | Keep backward compat with existing YAML configs |
| **Data quality (UT measurements)** | High | High | Robust validation in `grid_parser.py`: outlier detection, range checks, flag high-uncertainty interpolated regions |
| **Over-reliance on automated verdict** | Medium | High | Reports must highlight assumptions, governing criteria, and flag near-limit cases requiring expert engineering review |
| **Units mismatch (inch vs mm)** | Medium | Medium | All internal calculations in consistent units (default: inches); provide mm input/output conversion in `grid_parser.py` and `ffs_report.py` |
| **Duplication with existing code** | Medium | Medium | New `assessment/` stack delegates to existing `API579_components.py` for calculations; Phase 0 audit determines refactor strategy |

---

## Dependency Map

```
Phase 0 (Examples & Audit)  ← hard prerequisite for all
    │
    ├──► Phase 1 (Grid Accept/Reject)    ← core user ask, independent
    │
    ├──► Phase 2 (Industry Presets)      ← independent (extends t_min for new component types)
    │
    ├──► Phase 3 (Lifecycle)             ← independent (uses existing t_min for pipelines)
    │
    └──► Phase 4 (Integration & Polish)  ← requires Phases 1-3 complete
```

Phase 0 is a hard prerequisite. **Phases 1, 2, and 3 are independently startable** after Phase 0 — existing t_min logic works for pipeline lifecycle analysis (Phase 3) without needing Phase 2's expanded component types. Phase 2 extends Phase 1's assessment for new component types, but Phase 1 is fully functional for pipes alone. Phase 4 integrates all three.

---

## File Impact Summary

| Area | New Files | Modified Files |
|------|-----------|---------------|
| **Phase 0** | 3 example scripts | `basic_usage.py`, brochure, test files |
| **Phase 1** | 7 files in `assessment/` | `engine.py` (routing), `data.py` (CSV support) |
| **Phase 2** | 8 files in `industry/` + 4 YAML presets | `API579_components.py` (component types) |
| **Phase 3** | 5 files in `lifecycle/` | `API579_components.py` (trending hooks) |
| **Phase 4** | 0 | `__init__.py`, `__main__.py`, brochure |
| **Total** | ~23 new files | ~8 modified files |

Estimated new code: ~3,200 lines implementation + ~1,800 lines tests = ~5,000 lines total.

---

## Standards Reference

| Standard | Edition | Used In |
|----------|---------|---------|
| API 579-1/ASME FFS-1 | 2021 3rd Ed | Parts 4, 5 assessment flowcharts (Phase 1); general framework |
| ASME BPVC Section VIII | 2023 | Div 1/2 t_min (Phase 2) |
| ASME B31.4 | 2022 | Liquid pipeline (existing + Phase 2) |
| ASME B31.8 | 2022 | Gas pipeline (existing + Phase 2) |
| ASME B31.3 | 2022 | Process piping (Phase 2) |
| ASME B31G | 2023 | Modified B31G (existing) |
| DNV-RP-F101 | 2021 | Corroded pipeline (Phase 2) |
| BS 7910 | 2019+A1:2020 | Crack assessment (existing) |
| API 510 | 2022 | Vessel inspection intervals (Phase 3) |
| API 570 | 2020 | Piping inspection intervals (Phase 3) |
| API 653 | 2014 R2020 | Tank inspection intervals (Phase 3) |

---

## Future Work (Not In This Roadmap)

These are explicitly out of scope for WRK-138 but noted for future WRK items:

| Feature | Rationale for Deferral |
|---------|----------------------|
| Part 6: Pitting Corrosion | Separate WRK item, extends Phase 1 framework |
| Part 7: HIC/SOHIC | Specialist mechanism, refinery-specific |
| Part 10: Creep Damage | High-temperature niche, needs material creep data |
| Part 11: Fire Damage | Incident-driven, not routine |
| Part 12: Dents & Gouges | Mechanical damage, pipeline-specific |
| Part 13: Laminations | Rare manufacturing defect |
| Part 14: Fatigue | Cyclic loading, overlaps with existing fatigue module |
| Level 3 FEA | Requires FEA integration (Abaqus/Ansys/FreeCAD) |
| ML corrosion prediction | Needs large training dataset from inspections |
| ILI data import | Pipeline-specific vendor formats (Baker Hughes, Rosen) |
| RBI integration | Risk-based inspection is a separate discipline |
| CMMS integration | SAP/Maximo API is deployment-specific |

---

## Glossary

| Term | Definition |
|------|-----------|
| **CML** | Condition Monitoring Location — fixed UT measurement point |
| **FCA** | Future Corrosion Allowance — projected metal loss over interval |
| **FFS** | Fitness-for-Service — assessment of degraded equipment |
| **GML** | General Metal Loss — uniform corrosion over large area |
| **LML** | Local Metal Loss — localized corrosion in specific region |
| **MAWP** | Maximum Allowable Working Pressure |
| **RSF** | Remaining Strength Factor — ratio of degraded to undamaged strength |
| **t_min** | Minimum required wall thickness per design code |
| **t_mm** | Minimum measured thickness from inspection |
| **t_am** | Average measured thickness over assessment length |
| **UT** | Ultrasonic Testing — NDT method for wall thickness measurement |

---

## Review Log

| Iter | Date | Reviewer | Verdict | Findings | Fixed |
|------|------|----------|---------|----------|-------|
| R1 | 2026-02-13 | Claude Opus 4.6 | MINOR | 14: BS 7910 misattribution, B31G broken import, Part 6 contradiction, line count optimism, dependency chain, sham tests, legal scan, units strategy, remaining life overstated, test infra, basic_usage.py, material DB, Part 2 ref, CML uncertainty | 14/14 |
| R1 | 2026-02-13 | Codex CLI | MAJOR | 10: Part 6 scope contradiction, outdated standards refs, Part 2 oversimplification, heuristic router criteria, dependency chain, line count estimates, test count, missing workflows (applicability/QA/QC), missing Parts 3/8, duplication risk | 8/10 (2 deferred) |
| R1 | 2026-02-13 | Gemini CLI | MINOR | 4 categories: API 579 classification refinement, 3 missing risks (data quality/engineering judgment/user error), line count underestimates, missing O&G workflows (internal/external corrosion, HIC, composite repair, ILI, probabilistic) | 6/~12 (6 deferred to future WRK) |

**Deferred Items** (accepted as out-of-scope, documented in Future Work):
- Part 3 brittle fracture, Part 8 weld misalignment → future WRK items
- Applicability screening flow, data QA/QC, equation provenance → Phase 4 polish
- CML interpolation uncertainty flagging → Phase 4 polish
- Composite repair (ASME PCC-2), ILI vendor formats, probabilistic FFS → future WRK items

---

*Plan generated: 2026-02-13 | Template: workspace-hub plan template v1.0*
*Cross-review R1: 2026-02-13 | All findings addressed or deferred with rationale*
