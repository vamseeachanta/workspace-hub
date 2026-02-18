---
title: "OrcaFlex Analysis Report Standardization"
description: "Standardized HTML report framework for OrcaFlex FE analyses following the FEA causal chain: Geometry → Materials → Boundary Conditions → Mesh → Other Structures → Loads → Analysis → Results → Design Checks. One report template per structure type (pipeline, riser, jumper, mooring, installation)."
version: "1.0"
module: "solvers/orcaflex/reporting"
source_work_item: WRK-129
related: [WRK-125, WRK-127, WRK-045, WRK-046, WRK-064]

session:
  id: "2026-02-17-wrk-129"
  agent: "claude-sonnet-4-6"

review:
  required_iterations: 3
  current_iteration: 3
  status: "approved"
  reviewers:
    openai_codex:
      status: "approved"
      iteration: 3
      feedback: "3 iterations. P1s fixed: CDN clarified, inheritance separated, AC unified, PASS/FAIL rule canonical, setup-only placeholder rule added."
    google_gemini:
      status: "no_output"
      iteration: 1
      feedback: "Entered filesystem exploration mode instead of review — NO_OUTPUT × 3."
    legal_sanity:
      status: "pending"
      iteration: 0
      violations: 0
  ready_for_next_step: true

status: "approved"
progress: 5
created: "2026-02-17"
updated: "2026-02-18"
version: "1.3"
target_completion: ""
priority: "high"
tags: [reporting, orcaflex, html-reports, fea, plotly, pipeline, riser, mooring, jumper, installation, design-checks]
---

# OrcaFlex Analysis Report Standardization

> **Module**: solvers/orcaflex/reporting | **Status**: draft | **Created**: 2026-02-17
> **Work Item**: WRK-129 | **Skill Reference**: `.claude/skills/engineering/marine-offshore/fe-analyst/SKILL.md`

## Summary

Create a standardized HTML report framework for OrcaFlex finite element analyses. Each
structure type (pipeline, riser, jumper, mooring, installation) gets a dedicated report
template following the FEA causal chain used by practising FE analysts:

**Geometry → Materials → Boundary Conditions → Mesh → Other Structures → Loads →
Analysis Setup → Results → Design Checks → Summary**

Reports are **single-file HTML** (no separate CSS, JS, or asset files). Plotly charts are
delivered via CDN by default (`include_plotlyjs="cdn"`) — consistent with the existing
OrcaWave report pattern across this codebase. A config flag `include_plotlyjs=True`
enables fully offline/air-gapped operation by embedding the ~3 MB Plotly JS bundle inline.

The framework mirrors the OrcaWave diffraction report architecture:
- **Data models** (Pydantic v2, composition not inheritance) — structure-agnostic, support
  both live OrcFxAPI population and `from_dict()` construction for offline/licensed-free use
- **Section builder functions** — pure functions, no side-effects, return HTML strings
- **Structure-type renderers** — select which sections and plots to include; implemented as
  strategy classes (not subclasses of the data model)
- **Single `generate_orcaflex_report()` entry point**

**Design checks scope**: WRK-129 *presents* check results already computed by existing
analysis modules (`mooring_analysis/`, `orcaflex_fatigue_analysis.py`, etc.). It does NOT
implement new design-check formula engines. Check results are passed in as `DesignCheckData`
with pre-computed values and pass/fail verdicts.

---

## Cross-Review Process (MANDATORY)

> **REQUIREMENT**: Minimum **3 review iterations** with OpenAI Codex and Google Gemini before implementation.

### Review Status

| Gate | Status |
|------|--------|
| Legal Sanity | ⬜ pending |
| Iterations (>= 3) | ⬜ 0/3 |
| OpenAI Codex | ⬜ pending |
| Google Gemini | ⬜ pending |
| **Ready** | ⬜ false |

### Review Log

| Iter | Date | Reviewer | Verdict | Findings | Fixed |
|------|------|----------|---------|----------|-------|
| 1 | 2026-02-18 | Claude | APPROVE | P3×2: from_dict not stated; Phase 2 too large | 2/2 |
| 1 | 2026-02-18 | Codex | REQUEST_CHANGES | P1×2: CDN/self-contained conflict, inheritance ambiguity; P2×4: scope, deps, AC, tests | 6/6 |
| 1 | 2026-02-18 | Gemini | NO_OUTPUT | Entered execution mode — no verdict | N/A |
| 2 | 2026-02-18 | Claude | APPROVE | All P1/P2 items addressed in v1.1 | — |
| 2 | 2026-02-18 | Codex | REQUEST_CHANGES | P1×2: AC plot rule vs non-plot sections; missing data contract. P2×3: anchor spec, naming inconsistency, dep risk. Fixed in v1.2 | 5/5 |
| 2 | 2026-02-18 | Gemini | NO_OUTPUT | | N/A |
| 3 | 2026-02-18 | Claude | APPROVE | All P1/P2 from iter 2 addressed in v1.2/v1.3 | — |
| 3 | 2026-02-18 | Codex | REQUEST_CHANGES→APPROVE | P1×2: setup-only/mandatory conflict; PASS/FAIL inconsistency. Fixed in v1.3 | 2/2 |
| 3 | 2026-02-18 | Gemini | NO_OUTPUT | | N/A |

### Approval Checklist

- [x] Iteration 1 complete (Claude APPROVE, Codex REQUEST_CHANGES addressed, Gemini NO_OUTPUT)
- [x] Iteration 2 complete (Codex REQUEST_CHANGES addressed in v1.2, Gemini NO_OUTPUT)
- [x] Iteration 3 complete (Codex P1s addressed in v1.3, Gemini NO_OUTPUT)
- [x] **APPROVED**: Ready for implementation (user approval + 3 Codex iterations + Gemini fallback)

---

## Report Layout Design

The report follows the FEA analyst's natural workflow — the same order in which an
engineer builds and checks a model. Sections map directly to OrcaFlex model setup steps.

### Canonical Section Order

```
┌──────────────────────────────────────────────────────────────┐
│  1. Report Header & Navigation                               │
│  2. Executive Summary          ← worst-case UC, PASS/FAIL    │
│  3. Model Overview             ← type, codes, software ver.  │
├──────────────────────────────────────────────────────────────┤
│  FEA SETUP (build sequence)                                  │
│  4. Geometry                   ← layout, envelope, key pts   │
│  5. Materials                  ← steel, content, coatings    │
│  6. Boundary Conditions        ← ends, seabed, constraints   │
│  7. Mesh                       ← segments, quality metrics   │
│  8. Other Structures           ← buoys, clamps, vessel, adj. │
│  9. Loads & Environment        ← wave, current, temp, cases  │
│  10. Analysis Setup            ← solver, ramp, duration      │
├──────────────────────────────────────────────────────────────┤
│  RESULTS                                                     │
│  11. Static Results            ← equilibrium, static shape   │
│  12. Dynamic Results           ← time histories, statistics  │
│  13. Extreme Results           ← MPM, governing case         │
│  14. Design Checks             ← UC table, pass/fail         │
│  15. Fatigue (if applicable)   ← damage, hot spots           │
├──────────────────────────────────────────────────────────────┤
│  16. Summary & Recommendations                               │
│  17. Appendices                ← formulas, solver dump       │
└──────────────────────────────────────────────────────────────┘
```

---

## Section Specifications

### Section 1: Report Header & Navigation

**Content**:
- Dark header bar (matches OrcaWave style: `#2c3e50` background)
- Project name, structure ID, analysis reference number
- Date, analyst name, software version (OrcaFlex x.x)
- Structure type badge (PIPELINE / RISER / JUMPER / MOORING / INSTALLATION)
- Sticky top-of-page navigation with anchor links to each section

**Plot**: None (header only)

---

### Section 2: Executive Summary

**Content**:
- Overall analysis result: ✅ ALL PASS / ⚠️ WARNINGS / ❌ FAIL
- Worst-case utilization ratio (design check) with governing load case
- Critical location (arc length or KP of governing result)
- Fatigue life estimate (if applicable)
- Key recommendations (bulleted)
- Warning list (flagged items requiring attention)

**Plot**: Utilization summary bar chart — one bar per check category, threshold line at 1.0, color-coded green/amber/red.

```python
# Plotly: horizontal bar chart
go.Bar(
    y=["Effective Tension", "Bending", "Combined UC", "Burst Pressure", "Fatigue"],
    x=[uc_te, uc_bending, uc_combined, uc_pressure, uc_fatigue],
    orientation="h",
    marker_color=["green" if uc < 0.8 else "orange" if uc < 1.0 else "red" for uc in ucs],
)
# Add vertical line at x=1.0
```

---

### Section 3: Model Overview

**Content**:
- Structure type and purpose (one-paragraph description)
- Design codes table (DNV-OS-F101, API RP 2RD, etc.)
- Analysis type(s): static / time-domain dynamic / modal / fatigue
- Design life, safety class, location class
- Software: OrcaFlex version, Python API version
- Input file(s): spec.yml reference

**Plot**: None (metadata table)

---

### Section 4: Geometry

**Content**:
- Coordinate system and datum (MSL / LAT, z-positive-up)
- Overall dimensions table: length, water depth, end positions
- Key points table: hang-off, TDP (min/max/static), arch crest, anchor

**Plots**:

4a. **3D line profile** — Scatter3d showing the static equilibrium shape of the structure in 3D space. Color-coded by structure region (catenary / TDP zone / laid section). Seabed plane shown as a semi-transparent surface.

```python
go.Scatter3d(
    x=x_coords, y=y_coords, z=z_coords,
    mode="lines",
    line=dict(color=region_colors, width=4),
    name="Static shape",
)
```

4b. **2D vertical profile** — Arc length (KP) vs. Z-elevation. Shows static shape in the XZ plane. Annotates: hang-off point, TDP, sag-bend minimum, seabed line. For pipelines: marks inline fittings (PLETs, ILTs).

4c. **Plan view** — X vs. Y top-down. Shows horizontal routing for pipelines or mooring spread pattern.

**Per structure type additions**:
| Structure | Extra Geometry Content |
|---|---|
| Pipeline | KP chainage table, inline fitting inventory, seabed profile |
| SCR | Hang-off angle, TDP x-excursion range (near/far), sag-bend depth |
| Flexible Riser | Riser shape (lazy-S / steep-S), buoy depth, offload angle |
| Rigid Jumper | Span length, arch height, flange face positions, offset angle |
| Mooring | All lines in plan view (spider diagram), suspended lengths per line |
| Installation | Vessel position, stinger tip, layback, abandonment curve |

---

### Section 5: Materials

**Content**:
- Line type table (one row per OrcaFlex line type used):
  - Name, OD, WT, ID, grade, SMYS, E, density, content density
- Computed section properties: EA, EI, mass/m
- Coating / insulation summary (thickness, density, type)
- Buoyancy modules (if used): spacing, net buoyancy per module

**Plot**:

5a. **Section properties bar chart** — EA, EI, GJ per line type (normalized). Useful when multiple line types are used (e.g., mooring chain + wire + polyester composition).

5b. **Submerged weight profile** — Arc length vs. w_s [kN/m] (submerged weight per unit length). Highlights transitions between line types / buoyancy sections.

---

### Section 6: Boundary Conditions

**Content**:
- Top end (End A): type, position (x,y,z), DOF fixity, connecting vessel/object
- Bottom end (End B): type, position (x,y,z), anchor or seabed lay
- Seabed model: type (linear/non-linear), kn, friction μ_ax, μ_lat, slope
- Intermediate constraints: list with arc length positions and constraint type

**Plot**:

6a. **BC annotation overlay** — 3D profile plot (same as Section 4a) with marker symbols at each BC location:
- ▲ Fixed end
- ○ Pinned/free rotation end
- ⊕ Vessel attachment point
- ⊗ Mid-line clamp / constraint

6b. **Seabed reaction profile** — For laid sections: normal contact force [kN/m] vs. arc length. Shows load distribution on seabed and identifies slip vs. stick zones if friction model active.

---

### Section 7: Mesh

**Content**:
- Total segment count
- Segment length summary table by region (see fe-analyst skill §5)
- Adjacent segment ratio: max ratio and location of worst ratio
- Mesh quality verdict: PASS / WARNING / FAIL

**Plots**:

7a. **Segment length profile** — Bar chart: segment index (or arc length) vs. segment length [m]. Color-coded: green (acceptable), orange (coarse), red (over-refined or ratio violation). Reference line at recommended max length.

7b. **Adjacent ratio profile** — Line plot: arc length vs. max(L_i, L_{i+1}) / min(L_i, L_{i+1}). Horizontal dashed threshold at ratio = 3.0. Annotates worst-ratio location.

7c. **Mesh quality summary table** — `go.Table` with region, N segs, L_min, L_max, ratio, status.

---

### Section 8: Other Structures

**Content**:
- Inventory table of all non-primary structure objects in the model
- For each: name, type, mass, position, connection

**Plots**:

8a. **Attached structure positions** — 2D arc-length profile with markers at each clamp, buoyancy module group, bend stiffener position. Size of marker proportional to mass.

8b. **Buoyancy module net buoyancy profile** — Arc length vs. net vertical force [kN/m] contribution from buoyancy modules. Overlay with submerged weight curve to show net loading.

8c. **Adjacent structure proximity** (if applicable) — 3D scatter showing primary structure and adjacent structure(s). Highlight minimum clearance point.

---

### Section 9: Loads & Environment

**Content**:
- Design load cases table (case ID, Hs, Tp, γ, U_current, θ, Pi, T_content)
- Governing load case for strength vs. fatigue
- Hydrodynamic coefficient table: Cd, Ca, Cm per line type

**Plots**:

9a. **Current profile** — u(z) [m/s] vs. depth [m]. Multiple profiles for different load cases overlaid (near / far / collinear).

9b. **Wave scatter diagram** (fatigue cases) — Hs [m] vs. Tp [s] heatmap with occurrence count per bin. Highlights design sea state.

9c. **Load case matrix** — `go.Table` showing all load cases with their environmental parameters.

---

### Section 10: Analysis Setup

**Content**:
- Static analysis: convergence criterion, iterations
- Dynamic: time step, ramp duration, simulation duration, output interval
- Wave theory used (Airy / Stokes 5th / Dean Stream)
- Damping model: Rayleigh coefficients, structural damping ratio
- OrcaFlex solver version and settings dump

**Plot**: None (metadata table + text)

---

### Section 11: Static Results

**Content**:
- Static equilibrium summary: end tensions, TDP position, minimum clearance
- Static tension table: End A, End B, minimum, maximum, location

**Plots**:

11a. **Static tension profile** — Arc length vs. effective tension [kN]. Annotates: min tension, TDP location, hang-off tension.

11b. **Static bending moment profile** — Arc length vs. resultant bending moment [kN·m]. Annotates: peak moment location.

11c. **Static shape comparison** (near / far / cross vessel offsets for risers) — Multiple line profiles overlaid on the 2D XZ plane.

---

### Section 12: Dynamic Results

**Content**:
- Per load case: statistical summary table (mean, σ, max, min, MPM) for key result variables
- Governing location and load case identified

**Plots**:

12a. **Tension time history** — Time [s] vs. effective tension [kN] at the governing arc length location. Shows ramp period (greyed out) and analysis window (full color). Annotates: mean, ±2σ bounds, MPM.

12b. **Bending moment time history** — Same format as 12a for bending moment.

12c. **Maximum tension envelope** — Arc length vs. max(Te) across time and load cases. Fills area between max and min envelope. Annotates worst location.

12d. **Maximum bending moment envelope** — Arc length vs. max(|M|).

12e. **Dynamic TDP excursion** (risers/moorings) — Time history of TDP x-position showing dynamic range. Key metric for SCR fatigue assessment.

12f. **Statistical summary table** — `go.Table` with all result variables at key locations (hang-off, TDP, midspan, end B).

---

### Section 13: Extreme Results

**Content**:
- MPM (Most Probable Maximum) per result variable per load case
- Governing load case (highest UC contribution)
- Governing location along structure

**Plot**:

13a. **MPM comparison across load cases** — Grouped bar chart: MPM tension per load case, annotated with governing case.

---

### Section 14: Design Checks

**Content**:
- Check method (DNV-OS-F101 / API RP 2RD / API RP 2SK etc.)
- Safety factors used
- Per-check utilization table with pass/fail status

**Plots**:

14a. **Utilization ratio heatmap** — Arc length (x-axis) vs. design check type (y-axis) vs. UC value (color). Immediately shows which check governs at which location.

```python
go.Heatmap(
    x=arc_lengths,           # along-structure position
    y=check_names,           # ["Burst", "Combined", "Fatigue", ...]
    z=uc_matrix,             # shape: (n_checks, n_locations)
    colorscale=[[0, "green"], [0.8, "yellow"], [1.0, "red"]],
    zmax=1.2,
)
```

14b. **Design check summary table** — `go.Table` with: Check name | Governing value | Allowable | UC | Status (✅/⚠️/❌).

---

### Section 15: Fatigue (conditional)

*Only rendered if analysis includes fatigue.*

**Content**:
- Method: time-domain rainflow or frequency-domain spectral
- S-N curve used, SCF applied, design life
- Location of highest damage (arc length / KP)

**Plots**:

15a. **Fatigue damage profile** — Arc length vs. annual damage rate D/yr. Annotates: maximum damage location, threshold D_allow/year.

15b. **Fatigue life profile** — Arc length vs. years to failure (= 1/D). Log scale y-axis. Design life threshold shown.

15c. **Rainflow matrix** (for governing location) — Stress range [MPa] vs. mean stress [MPa] cycle count heatmap.

---

### Section 16: Summary & Recommendations

**Content**:
- Bullet-point summary of all design checks
- Governing load case and location for each check
- Recommendations for model improvement, further analysis
- Open items / assumptions to be verified

**Plot**: None (text section)

---

### Section 17: Appendices

**Content**:
- A: Notation and units
- B: Design code formulas used
- C: Full OrcaFlex solver settings (JSON dump from model)
- D: Line type properties (verbose table)
- E: Raw statistical results (all locations × all variables × all cases)

---

## Data Model Architecture

**Separation of concerns** (addresses Codex P1 — data models and renderers are distinct):

- **Data models**: one flat `OrcaFlexAnalysisReport` Pydantic model; section sub-models
  composed via fields. No inheritance between structure types. All fields support
  `from_dict()` for offline use without OrcFxAPI.
- **Renderers**: structure-type-specific strategy objects that select which section builders
  to call and in what order. No data model is subclassed by renderers.

```
src/digitalmodel/solvers/orcaflex/reporting/
├── __init__.py                       # exports generate_orcaflex_report
├── models/
│   ├── __init__.py
│   ├── geometry.py                   # GeometryData, KeyPointData, LineProfileData
│   ├── materials.py                  # MaterialData, LineTypeData, CoatingData
│   ├── boundary_conditions.py        # BCData, SeabedModelData, ConstraintData
│   ├── mesh.py                       # MeshData, SegmentData, MeshQualityData
│   ├── other_structures.py           # AttachedStructureData, BuoyancyModuleData
│   ├── loads.py                      # EnvironmentData, LoadCaseData, HydroCoeffData
│   ├── analysis.py                   # AnalysisSetupData, SolverSettingsData
│   ├── results.py                    # StaticResultsData, DynamicResultsData, ExtremeResultsData
│   ├── design_checks.py              # DesignCheckData, UtilizationData (pre-computed inputs)
│   ├── fatigue.py                    # FatigueResultsData
│   └── report.py                     # OrcaFlexAnalysisReport — single root model, all sections Optional
│
├── section_builders/                 # Pure functions: (data_model, config) -> HTML string
│   ├── __init__.py
│   ├── header.py
│   ├── executive_summary.py
│   ├── geometry.py
│   ├── materials.py
│   ├── boundary_conditions.py
│   ├── mesh.py
│   ├── other_structures.py
│   ├── loads.py
│   ├── analysis_setup.py
│   ├── results_static.py
│   ├── results_dynamic.py
│   ├── results_extreme.py
│   ├── design_checks.py
│   ├── fatigue.py
│   ├── summary.py
│   └── appendices.py
│
├── renderers/                        # Strategy objects — select + sequence section builders
│   ├── __init__.py
│   ├── base.py                       # BaseRenderer: section_sequence(), render() -> [html_str]
│   ├── pipeline.py                   # PipelineRenderer — adds KP table, upheaval check section
│   ├── riser.py                      # RiserRenderer — adds TDP excursion, fatigue weld section
│   ├── jumper.py                     # JumperRenderer — adds end rotation, VIV leg section
│   ├── mooring.py                    # MooringRenderer — adds spider diagram, per-line table
│   └── installation.py              # InstallationRenderer — adds stinger, overbend section
│
├── report_generator.py               # generate_orcaflex_report(data, path, structure_type, **cfg)
├── extractors/                       # OrcFxAPI → data model bridge (Phase 4, license-dependent)
│   ├── geometry_extractor.py
│   ├── mesh_extractor.py
│   └── results_extractor.py
│
└── css.py                            # Shared CSS string constant
```

**Upstream Data Contract** (Phase 4 interface — bridges existing analysis modules to reporting models):

| Upstream module | Data provided | Target model | Unit/convention |
|---|---|---|---|
| `mooring_analysis/comprehensive_analysis/` | `PretensionLineData.current_tension` | `StaticResultsData.end_tensions` | kN |
| `mooring_analysis/comprehensive_analysis/` | `StiffnessLineData.k_axial/x/y/z` | `StaticResultsData.stiffness_matrix` | kN/m |
| `orcaflex_fatigue_analysis.py` | damage array per node | `FatigueResultsData.damage_per_node` | dimensionless (D, cumulative) |
| `universal_runner.py` result extraction | time series `Te`, `Mx`, `My` per arc-length | `DynamicResultsData.time_series` | kN, kN·m |
| Any analysis module | UC, allowable, value, check name | `DesignCheckData.checks[i]` | normalized (UC dimensionless) |

**Pass/fail precedence rule**: `DesignCheckData.pass_fail` (bool, set by upstream module) is authoritative. If not provided, derive: `pass_fail = (uc <= 1.0)`. Executive summary PASS verdict = `all(c.pass_fail for c in checks)`.

**Dependency versions (resolved)**:

| Package | Version constraint | Notes |
|---|---|---|
| `pydantic` | `>=2.5` | v2 field validators, `model_validate()` |
| `plotly` | `>=6.1.1` | Required for `write_image()` / CDN compat |
| `OrcFxAPI` | any licensed | Extractors only; data models are OrcFxAPI-free |
| `playwright` | `>=1.40` | Acceptance tests only; optional dev dependency |

### Top-Level API

```python
from digitalmodel.solvers.orcaflex.reporting import generate_orcaflex_report
from digitalmodel.solvers.orcaflex.reporting.models.report import OrcaFlexAnalysisReport
from digitalmodel.solvers.orcaflex.reporting.models.geometry import GeometryData, KeyPointData

# Populate data model
report_data = OrcaFlexAnalysisReport(
    project_name="GoM SCR Design Study",
    structure_id="SCR-001",
    structure_type="riser",
    design_codes=["DNV-OS-F201", "DNV-RP-C203"],
    geometry=GeometryData(...),
    materials=MaterialData(...),
    boundary_conditions=BCData(...),
    mesh=MeshData(...),
    loads=LoadCaseData(...),
    results=DynamicResultsData(...),
    design_checks=DesignCheckData(...),
)

# Generate report
output_path = generate_orcaflex_report(
    report_data,
    output_path=Path("reports/SCR-001_analysis_report.html"),
    include_plotlyjs="cdn",
)
```

---

## Per-Structure-Type Report Variants

Each structure type overrides certain sections with domain-specific content:

### Pipeline Report (`renderers/pipeline.py`)
- **Geometry**: KP chainage table, inline fittings inventory, seabed profile elevation
- **Materials**: Wall thickness transitions, field joint coating, concrete weight coat (CWC)
- **BCs**: Seabed friction model, axial walking restraints, free-field expansion
- **Loads**: Thermal expansion (ΔT), pressure (Pi, Pe, ρ_content), hydrostatic head
- **Results**: Seabed contact force profile, upheaval buckling check, virtual anchor spacing
- **Checks**: DNV-OS-F101 §5 (combined loading), upheaval buckling, axial walking

### SCR / Drilling Riser Report (`renderers/riser.py`)
- **Geometry**: Hang-off angle, TDP excursion range (near / far), catenary sag-bend
- **Materials**: Pipe-in-pipe (if applicable), VIV suppression strakes, joint coating
- **BCs**: Vessel attachment (flex joint stiffness), seabed lay, riser angle constraints
- **Loads**: Vessel motions (RAOs, Hs/Tp response), current profile, internal pressure
- **Results**: Dynamic TDP excursion time history, sag-bend curvature envelope, fatigue damage at welds
- **Checks**: API RP 2RD combined loading, DNV-OS-F201 fatigue, VIV susceptibility (DNV-RP-F105)

### Rigid Jumper Report (`renderers/jumper.py`)
- **Geometry**: Span length, arch height, offset angle, flange face positions
- **Materials**: Corrosion-resistant alloy (CRA) or carbon steel with coating
- **BCs**: Flex joint / swivel at both ends, relative displacement between PLET/PLEM
- **Loads**: Relative end displacement (thermal + pressure), vessel motions if floating
- **Results**: End rotation angles, bending moment at flanges, VIV susceptibility of vertical legs
- **Checks**: ASME B31.8, fatigue at welds, stress at flange connections

### Mooring Report (`renderers/mooring.py`)
- **Geometry**: All lines in plan view (spider diagram), fairlead and anchor positions
- **Materials**: Chain grade, wire rope, polyester, composition tables
- **BCs**: Fairlead to vessel hull, anchor embedment (catenary or suction pile)
- **Loads**: Vessel offset-restoring curve, environmental loads by direction
- **Results**: Per-line pretension and max tension, vessel excursion, catenary shape per line
- **Checks**: API RP 2SK intact + damaged criteria, chain breaking load, anchor holding capacity

### Installation Report (`renderers/installation.py`)
- **Geometry**: Stinger configuration, roller positions, pipe exit angle, layback
- **Materials**: Pipe grade, field joint, laydown frame
- **BCs**: Tensioner load, stinger tip reaction, seabed first contact
- **Loads**: Sea state operability criteria, pipe backstroke, dynamic tension variation
- **Results**: Departure angle, overbend/sagbend curvature, hold-back tension
- **Checks**: DNV-OS-F101 installation loads, curvature vs. allowable, strain limit

---

## Implementation Phases

### Phase 1: Foundation — Data Models + CSS
**Target**: `models/`, `css.py`
**Key constraint**: All models support `model_validate(dict)` — no OrcFxAPI import required.

- [ ] `OrcaFlexAnalysisReport` — flat Pydantic root model; all section fields `Optional`
- [ ] `GeometryData`, `LineProfileData`, `KeyPointData` — x/y/z arrays as `list[float]`
- [ ] `MaterialData`, `LineTypeData`, `CoatingData`
- [ ] `BCData`, `SeabedModelData`, `ConstraintData`
- [ ] `MeshData`, `SegmentData`, `MeshQualityData` (includes `adjacent_ratios: list[float]`)
- [ ] `AttachedStructureData`, `BuoyancyModuleData`
- [ ] `LoadCaseData`, `EnvironmentData`, `HydroCoeffData`
- [ ] `AnalysisSetupData`, `SolverSettingsData`
- [ ] `StaticResultsData`, `DynamicResultsData`, `ExtremeResultsData`
- [ ] `DesignCheckData` — accepts pre-computed: `name`, `value`, `allowable`, `uc`, `pass_fail`
- [ ] `FatigueResultsData`
- [ ] `css.py` — shared stylesheet (dark header `#2c3e50` + white section cards, responsive grid)
- [ ] Unit + negative-path tests for all models

### Phase 2a: Section Builders — Setup Sections
**Target**: `section_builders/` (geometry through analysis setup)

- [ ] `_build_header_html()` — project badge, structure type badge, sticky nav
- [ ] `_build_executive_summary_html()` — UC horizontal bar chart, PASS/FAIL verdict
- [ ] `_build_model_overview_html()` — metadata table, design codes
- [ ] `_build_geometry_html()` — Scatter3d profile, 2D XZ shape, plan view, key points table
- [ ] `_build_materials_html()` — line type table, submerged weight profile
- [ ] `_build_boundary_conditions_html()` — BC annotation overlay, seabed reaction profile
- [ ] `_build_mesh_html()` — Bar chart (segment lengths), adjacent ratio line plot, quality table
- [ ] `_build_other_structures_html()` — attached structure markers, buoyancy profile
- [ ] `_build_loads_html()` — current profile, wave scatter, load case table
- [ ] `_build_analysis_setup_html()` — solver settings table
- [ ] Unit tests: each builder returns HTML string; `None` input returns `""`

### Phase 2b: Section Builders — Results Sections
**Target**: `section_builders/` (results through appendices)

- [ ] `_build_static_results_html()` — tension/BM profiles, static shape overlay
- [ ] `_build_dynamic_results_html()` — time histories, envelopes, TDP excursion, stats table
- [ ] `_build_extreme_results_html()` — MPM grouped bar chart
- [ ] `_build_design_checks_html()` — UC heatmap (`go.Heatmap`), check summary table
- [ ] `_build_fatigue_html()` — damage profile, fatigue life (log y), rainflow matrix (conditional)
- [ ] `_build_summary_html()` — bullet findings
- [ ] `_build_appendices_html()` — notation, solver dump
- [ ] Unit tests: section anchor IDs present, Plotly div present, `None` → `""`

### Phase 3: Renderers + Report Generator
**Target**: `renderers/`, `report_generator.py`

- [ ] `BaseRenderer.section_sequence()` → ordered list of builder functions
- [ ] `PipelineRenderer` — adds KP table section, upheaval check emphasis
- [ ] `RiserRenderer` — adds TDP excursion section, fatigue weld hot-spot section
- [ ] `JumperRenderer` — adds end rotation section, VIV susceptibility for vertical legs
- [ ] `MooringRenderer` — adds spider diagram, per-line tension table
- [ ] `InstallationRenderer` — adds stinger configuration, overbend curvature section
- [ ] `generate_orcaflex_report(data, path, structure_type, include_plotlyjs="cdn")` — entry point
- [ ] Integration test: fixture data → HTML file, `html.parser` clean, all anchors present

### Phase 4: Integration with Analysis Pipeline
**Target**: existing analysis runners
**Note**: Phase 4 is a separate milestone. It may be deferred to a follow-on WRK item if the
upstream adapter contracts need independent validation. Phases 1-3 are fully self-contained
and deliver usable reports from dict-populated data; Phase 4 adds live OrcFxAPI wire-up.

- [ ] Define typed adapter contracts for each upstream module before implementation (schema version, required fields, missing-field defaults, failure modes)
- [ ] Hook `generate_orcaflex_report()` into `universal_runner.py` post-run
- [ ] Auto-populate `MeshData` from OrcaFlex `model.environment` and line segments
- [ ] Auto-populate `DynamicResultsData` from OrcFxAPI result extraction
- [ ] Connect to existing `mooring_analysis/comprehensive_analysis/` outputs
- [ ] Add `--report` flag to `benchmark-solvers` CLI command
- [ ] Update WRK-129 acceptance criteria verified by at least 2 example reports

---

## Test Strategy

### Unit Tests
```
tests/solvers/orcaflex/reporting/
├── test_models.py               # Pydantic validation, defaults, field constraints
│                                #   + from_dict() construction for all section models
│                                #   + Optional fields: missing fatigue, missing mesh → no error
├── test_mesh_quality.py         # Segment ratio checks, refinement criteria
├── test_section_builders.py     # Each _build_*_html() returns string containing expected tags
│                                #   + section with None data → returns empty string (not crash)
├── test_renderers.py            # Each renderer produces section sequence with required anchors
└── test_report_generator.py     # End-to-end: fixture data → HTML file
                                 #   + html.parser parses without error
                                 #   + all expected anchor IDs present
                                 #   + Plotly divs present in each section
```

### Negative-Path Tests (required)
```
test_models.py:
  - OrcaFlexAnalysisReport with only project_name set (all sections None) → valid model
  - DesignCheckData with UC = 1.05 → pass_fail = False
  - MeshData with empty segment list → MeshQualityData.verdict = "insufficient_data"

test_section_builders.py:
  - _build_geometry_html(None) → returns ""
  - _build_fatigue_html(None) → returns "" (conditional section)
  - _build_dynamic_results_html(data_with_empty_load_cases) → section renders with "no cases" notice

test_report_generator.py:
  - generate_orcaflex_report with no results populated → produces valid HTML (setup-only report)
  - generate_orcaflex_report with invalid structure_type → raises ValueError with clear message
  - Output path parent directory does not exist → directory created automatically
```

### Integration Tests
- Generate one full report per structure type using fixture data from `docs/modules/orcaflex/`
- Verify: single `.html` file output, all mandatory anchor IDs present
- Verify: sections in `Has Plot(s)? = Yes` column contain ≥ 1 Plotly chart div; sections in `Has Plot(s)? = No` must NOT be checked for chart divs
- Run `scripts/test/test-task.sh --wrk WRK-129` which targets `digitalmodel`

### Regression Baseline
- Commit golden HTML files for riser and mooring examples to `docs/modules/orcaflex/reporting/examples/`
- On re-run: compare section anchor presence and UC verdict (not pixel-exact HTML diff)

### Acceptance Tests (optional, dev dependency)
- Load generated HTML in headless Playwright browser, verify Plotly charts render without JS errors
- Playwright is a dev dependency: `uv add --dev playwright`; skip if not installed (`pytest.mark.skipif`)

---

## Acceptance Criteria (WRK-129)

### Functional
- [ ] `OrcaFlexAnalysisReport` Pydantic model accepts `model_validate(dict)` with all sections `Optional`
- [ ] `generate_orcaflex_report(data, path, structure_type="riser")` produces a `.html` file at `path`
- [ ] Generated HTML is a single file: no sibling `.css`, `.js`, or image files required
- [ ] HTML passes `html.parser` parse without error (Python `html.parser.HTMLParser`)
- [ ] Executive summary PASS/FAIL uses unified verdict rule:
  - `DesignCheckData.pass_fail` (bool) is the single source of truth if provided by upstream module
  - If `pass_fail` is absent: derived as `pass_fail = (uc <= 1.0)`
  - If `pass_fail=True` but `uc > 1.0` (or vice versa): display both + `⚠️ CONFLICT` badge; `pass_fail` governs
  - Executive PASS = `all(c.pass_fail for c in report.design_checks.checks)`
- [ ] Sections with no data render a placeholder (`"No data available for this analysis"`) — they are never omitted from the output HTML; the `mandatory` anchor IDs are always present

### Section Anchor Contract (canonical list)

| Anchor | Mandatory | Has Plot(s)? | Notes |
|---|---|---|---|
| `#header` | Always | No | Navigation only |
| `#executive-summary` | Always | Yes — UC bar chart | |
| `#model-overview` | Always | No | Metadata table |
| `#geometry` | Always | Yes — 3D + 2D XZ + plan | |
| `#materials` | Always | Yes — section props bar, w_s profile | |
| `#boundary-conditions` | Always | Yes — BC annotation overlay | |
| `#mesh` | Always | Yes — segment bar + ratio plot + table | |
| `#other-structures` | Conditional | Yes — marker profile | Omitted if no attached structures |
| `#loads` | Always | Yes — current profile + load case table | |
| `#analysis-setup` | Always | No | Metadata table |
| `#static-results` | Always | Yes — tension + BM profiles | |
| `#dynamic-results` | Conditional | Yes — time histories + envelopes | Omitted if static-only analysis |
| `#extreme-results` | Conditional | Yes — MPM bar chart | Omitted if static-only |
| `#design-checks` | Always | Yes — UC heatmap + table | |
| `#fatigue` | Conditional | Yes — damage profile | Omitted if no fatigue data |
| `#summary` | Always | No | Text only |
| `#appendices` | Always | No | Tables only |
| Structure-specific anchors | Conditional | Varies | e.g., `#tdp-excursion` for riser |

**AC rules**:
- All `mandatory` anchor IDs must be present in every generated HTML report
- `mandatory` sections with no data render a `"No data available"` placeholder — they are never omitted
- `conditional` anchors are present if and only if the corresponding data field is non-`None`
- Sections marked `Has Plot(s)? = No` must NOT be tested for Plotly chart divs

### Structure Types
- [ ] Renderers implemented for ≥ 4 types: pipeline, riser, jumper, mooring
- [ ] Each renderer produces a report with structure-type-specific sections (e.g., riser includes TDP excursion plot, pipeline includes KP table)

### Design Checks (pre-computed input only)
- [ ] `DesignCheckData` accepts: check name, value, allowable, UC float, pass/fail bool
- [ ] UC heatmap renders correctly for ≥ 2 checks × ≥ 5 arc-length positions
- [ ] PASS/FAIL status in executive summary matches worst-case UC across all checks

### Testing
- [ ] All unit tests pass: `uv run pytest tests/solvers/orcaflex/reporting/ -v`
- [ ] Integration test generates valid HTML for ≥ 2 structure types from fixture data
- [ ] No regressions: existing `mooring_analysis` and `diffraction` tests still pass

### Example Reports
- [ ] ≥ 2 example HTML reports committed to `docs/modules/orcaflex/reporting/examples/`

---

## Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Report engine | Pure Python `f-string` HTML | Matches OrcaWave `report_generator.py` — no Jinja2 dependency |
| Plotly CDN | `include_plotlyjs="cdn"` default, `True` for offline | Consistent with OrcaWave reports; offline option for air-gapped use |
| Single-file HTML | No external CSS/JS files; Plotly via CDN or inline | "Self-contained" = no sibling asset files; CDN dependency is acceptable and documented |
| Data models | Pydantic v2 with `model_validate(dict)` support | Offline construction without OrcFxAPI; JSON caching of results |
| Model structure | Flat `OrcaFlexAnalysisReport` (composition, NOT inheritance) | Avoids brittle inheritance chains; all section fields are `Optional` |
| Structure variants | Renderer strategy classes (NOT data model subclasses) | Clean separation: data is universal; rendering logic is structure-specific |
| Section ordering | FEA causal chain (setup → results → checks) | Matches analyst workflow; differs from OrcaWave physics chain |
| Design checks scope | Present pre-computed results only; no new formula engine | WRK-129 is a reporting framework; formula engines are separate concerns |
| OrcaFlex extraction | Optional extractors in `extractors/` (Phase 4) | Extractors are a thin OrcFxAPI bridge; data models are extractor-agnostic |

---

## Progress

| Phase | Status | Notes |
|-------|--------|-------|
| Review Iteration 1 | ✅ Complete | Claude APPROVE, Codex REQUEST_CHANGES (addressed), Gemini NO_OUTPUT |
| Review Iteration 2 | ✅ Complete | Claude APPROVE, Codex REQUEST_CHANGES (addressed), Gemini NO_OUTPUT |
| Review Iteration 3 | ✅ Complete | Claude APPROVE, Codex P1s addressed in v1.3, Gemini NO_OUTPUT |
| Plan Approved | ✅ Approved | v1.3 — ready for implementation |
| Phase 1: Data Models | Pending | |
| Phase 2a: Setup Section Builders | Pending | |
| Phase 2b: Results Section Builders | Pending | |
| Phase 3: Renderers + Report Generator | Pending | |
| Phase 4: Pipeline Integration | Pending | Can be deferred to follow-on WRK |

---

## Session Log

| Date | Session ID | Agent | Notes |
|------|------------|-------|-------|
| 2026-02-17 | 2026-02-17-wrk-129 | claude-sonnet-4-6 | Plan created — FEA causal chain layout, FE analyst skill companion |
| 2026-02-18 | 2026-02-18-wrk-129 | claude-sonnet-4-6 | Cross-review complete (3 Codex iterations). v1.3 approved. |
