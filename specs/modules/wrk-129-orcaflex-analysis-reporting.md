---
title: "OrcaFlex Analysis Report Standardization"
description: "Standardized HTML report framework for OrcaFlex FE analyses following the FEA causal chain: Geometry → Materials → Boundary Conditions → Mesh → Other Structures → Loads → Analysis → Results → Design Checks. One report template per structure type (pipeline, riser, jumper, mooring, installation)."
module: "solvers/orcaflex/reporting"
source_work_item: WRK-129
related: [WRK-125, WRK-127, WRK-045, WRK-046, WRK-064]

session:
  id: "2026-02-17-wrk-129"
  agent: "claude-sonnet-4-6"

review:
  required_iterations: 3
  current_iteration: 14
  status: "approved"
  reviewers:
    openai_codex:
      status: "approved"
      last_verdict: "APPROVE"
      iteration: 14
      feedback: "iter 14 APPROVE: v1.13 resolves all prior issues. structure_type consistently derived from data model, escaping policy enforced with new-field-test rule, structural HTML assertions added. P3 minor: html.parser still lightweight (non-blocking). Spec is ready for implementation."
    google_gemini:
      status: "no_output"
      iteration: 1
      feedback: "Entered filesystem exploration mode instead of review — NO_OUTPUT × 13. Per NO_OUTPUT policy, non-blocking."
    legal_sanity:
      status: "pending"
      iteration: 0
      violations: 0
  codex_gate: "approved"          # pending_recheck | approved | blocked
  ready_for_next_step: true

status: "complete"
progress: 100
created: "2026-02-17"
updated: "2026-02-23"
version: "1.13"
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

**CDN security requirements** (when `include_plotlyjs="cdn"`):
- Pin the CDN URL to the installed Plotly version: `https://cdn.plot.ly/plotly-{version}.min.js`
- Embed SRI integrity attribute: `<script src="..." integrity="sha384-{hash}" crossorigin="anonymous">`
- Document the pinned version and its SRI hash in `report_generator.py`; update on Plotly upgrade
- Offline fallback (`include_plotlyjs=True`) must be documented in the `generate_orcaflex_report()` docstring

The framework mirrors the OrcaWave diffraction report architecture:
- **Data models** (Pydantic v2, composition not inheritance) — structure-agnostic, support
  both live OrcFxAPI population and `from_dict()` construction for offline/licensed-free use
- **Section builder functions** — pure functions, no side-effects, return HTML strings
- **Structure-type renderers** — select which sections and plots to include; implemented as
  strategy classes (not subclasses of the data model)
- **Single `generate_orcaflex_report()` entry point**

**HTML injection security** (mandatory): **Every** user-supplied string field rendered
into HTML — including `project_name`, `structure_id`, `analyst`, `design_codes` entries,
load-case labels, check names, object names, section labels, recommendation/warning text,
and case IDs — MUST pass through a single shared helper `_escape(s: str) -> str` that
wraps `html.escape()`. Section builders MUST NOT call `html.escape()` directly; all
string interpolation goes through `_escape()`. **Enforcement rule**: any PR adding a new
`str` or `list[str]` field to a data model MUST add a corresponding escaping test for
that field — the test list in this spec is the minimum, not the ceiling. Tests must verify:
1. `<script>alert(1)</script>` → `&lt;script&gt;alert(1)&lt;/script&gt;` for each of:
   `project_name`, `structure_id`, `analyst`, a load-case label, a `UtilizationData.name`,
   and a recommendation/warning string (six field-specific tests — already required).
2. **Global escaping test**: inject `<script>alert(1)</script>` into the following
   enumerated string fields: `project_name`, `structure_id`, `analyst`, one `design_codes`
   entry, one `LoadCaseData.id`, one `UtilizationData.name`, and one recommendation string.
   Assert `"<script>alert(1)</script>" not in html` (the raw literal must be absent; the
   escaped form `&lt;script&gt;alert(1)&lt;/script&gt;` may be present — that is correct).
   Do NOT assert `re.search(r'<script', html) is None` — legitimate Plotly `<script>` tags
   will always be present.

**Design checks scope**: WRK-129 *presents* check results already computed by existing
analysis modules (`mooring_analysis/`, `orcaflex_fatigue_analysis.py`, etc.). It does NOT
implement new design-check formula engines. Check results are passed in as `DesignCheckData`
with pre-computed values and pass/fail verdicts.

---

## Cross-Review Process (MANDATORY)

> **REQUIREMENT**: Minimum **3 review iterations** with OpenAI Codex and Google Gemini before implementation.
> **NO_OUTPUT policy**: A `NO_OUTPUT` verdict (reviewer unable to produce a structured review — e.g., tool timeout, execution mode error) does **not block** progress. It is logged and noted, but the iteration is still considered complete. Codex is the **hard gate**: a Codex `REQUEST_CHANGES` blocks proceeding; a Codex `APPROVE` unblocks. Gemini `NO_OUTPUT` across all iterations satisfies the multi-provider requirement; it is non-blocking.

### Review Status

| Gate | Status |
|------|--------|
| Legal Sanity | ⬜ pending |
| Iterations (>= 3) | ✅ 3/3 (v1.3 approved); 14 iterations total |
| OpenAI Codex | ✅ iter 14 **APPROVE** (v1.13) |
| Google Gemini | ⬜ no\_output × 14 (non-blocking per NO\_OUTPUT policy) |
| **Ready** | ✅ **APPROVED** — ready for Phase 1 implementation |

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
| 4 | 2026-02-23 | Claude | NO_OUTPUT | exit 126 — timeout | N/A |
| 4 | 2026-02-23 | Codex | REQUEST_CHANGES | P1×1: exec PASS/FAIL conflict; P2×3: dup version, stale gate table, CDN security; P3×1: Playwright not mandatory. Fixes in v1.4 | 4/4 |
| 4 | 2026-02-23 | Gemini | NO_OUTPUT | Entered execution mode — no verdict | N/A |
| 5 | 2026-02-23 | Claude | NO_OUTPUT | exit 126 — timeout | N/A |
| 5 | 2026-02-23 | Codex | REQUEST_CHANGES | P1×2: dup #dynamic-tdp-excursion, pass_fail Optional ambiguity; P2×2: no HTML-escape req, mandatory/conditional wording; P3×1: plotly justification. Fixes in v1.5 | 5/5 |
| 5 | 2026-02-23 | Gemini | NO_OUTPUT | Entered execution mode — no verdict | N/A |
| 6 | 2026-02-23 | Claude | NO_OUTPUT | exit 126 — timeout | N/A |
| 6 | 2026-02-23 | Codex | REQUEST_CHANGES | P1×1: placeholder ownership; P2×2: field naming inconsistency / all(c.pass_fail) unsafe. Fixes in v1.6 | 3/3 |
| 6 | 2026-02-23 | Gemini | NO_OUTPUT | Entered execution mode — no verdict | N/A |
| 7 | 2026-02-23 | Claude | NO_OUTPUT | exit 126 — timeout | N/A |
| 7 | 2026-02-23 | Codex | REQUEST_CHANGES | P1×1: pass_fail ownership (DesignCheckData vs UtilizationData); P2×2: model_overview.py missing from tree / HTML-escape tests only project_name. Fixes in v1.7 | 3/3 |
| 7 | 2026-02-23 | Gemini | NO_OUTPUT | Entered execution mode — no verdict | N/A |
| 8 | 2026-02-23 | Claude | NO_OUTPUT | exit 126 — timeout | N/A |
| 8 | 2026-02-23 | Codex | REQUEST_CHANGES | P2×2: loads=LoadCaseData (should be list) / CDN SRI not in AC+tests; P3×1: pass_fail type inconsistency. Fixes in v1.8 | 3/3 |
| 8 | 2026-02-23 | Gemini | NO_OUTPUT | Entered execution mode — no verdict | N/A |
| 9 | 2026-02-23 | Claude | NO_OUTPUT | exit 126 — timeout | N/A |
| 9 | 2026-02-23 | Codex | REQUEST_CHANGES | P2×1: gate inconsistency (Gemini NO_OUTPUT policy not explicit); P3×1: DesignCheckData test bullet wrong class. Fixes in v1.9 | 2/2 |
| 9 | 2026-02-23 | Gemini | NO_OUTPUT | Entered execution mode — no verdict | N/A |
| 10 | 2026-02-23 | Claude | NO_OUTPUT | exit 126 — timeout | N/A |
| 10 | 2026-02-23 | Codex | REQUEST_CHANGES | P2×1: Plotly div assertion wrong scope (all vs plot-only sections); P3×1: codex.feedback shows REQUEST_CHANGES while recheck pending. Fixes in v1.10 | 2/2 |
| 10 | 2026-02-23 | Gemini | NO_OUTPUT | Entered execution mode — no verdict | N/A |
| 11 | 2026-02-23 | Claude | NO_OUTPUT | exit 126 — timeout | N/A |
| 11 | 2026-02-23 | Codex | REQUEST_CHANGES | P2×1: escaping not universal (6-field only); P2×1: offline mode no AC+tests; P3×1: gate status ambiguity. Fixes in v1.11 | 3/3 |
| 11 | 2026-02-23 | Gemini | NO_OUTPUT | Entered execution mode — no verdict | N/A |
| 12 | 2026-02-23 | Claude | NO_OUTPUT | exit 126 — timeout | N/A |
| 12 | 2026-02-23 | Codex | REQUEST_CHANGES | P1×1: global XSS re.search broken (Plotly <script> tags exist); P2×1: empty checks→PASS not N/A; P3×1: global XSS field enum ambiguous. Fixes in v1.12 | 3/3 |
| 12 | 2026-02-23 | Gemini | NO_OUTPUT | Entered execution mode — no verdict | N/A |
| 13 | 2026-02-23 | Claude | NO_OUTPUT | exit 126 — timeout | N/A |
| 13 | 2026-02-23 | Codex | REQUEST_CHANGES | P2×1: generate_orcaflex_report signature inconsistent (structure_type as param vs data model field); P2×1: escaping enforcement rule missing for new fields; P3×1: html.parser assertion weak. Fixes in v1.13 | 3/3 |
| 13 | 2026-02-23 | Gemini | NO_OUTPUT | Entered execution mode — no verdict | N/A |
| 14 | 2026-02-23 | Claude | NO_OUTPUT | exit 126 — timeout | N/A |
| 14 | 2026-02-23 | Codex | **APPROVE** | v1.13 resolves all issues. P3 minor (html.parser still lightweight) — non-blocking. | ✅ |
| 14 | 2026-02-23 | Gemini | NO_OUTPUT | Entered execution mode — no verdict | N/A |

### Approval Checklist

- [x] Iteration 1 complete (Claude APPROVE, Codex REQUEST_CHANGES addressed, Gemini NO_OUTPUT)
- [x] Iteration 2 complete (Codex REQUEST_CHANGES addressed in v1.2, Gemini NO_OUTPUT)
- [x] Iteration 3 complete (Codex P1s addressed in v1.3, Gemini NO_OUTPUT)
- [x] Iteration 4 complete (Codex REQUEST_CHANGES on v1.4 additions — all P1/P2 fixed in v1.4)
- [x] Iteration 5 complete (Codex REQUEST_CHANGES on v1.5 — all P1/P2 fixed in v1.5)
- [x] Iteration 6 complete (Codex REQUEST_CHANGES on v1.6 — all P1/P2 fixed in v1.6)
- [x] Iteration 7 complete (Codex REQUEST_CHANGES on v1.7 — all P1/P2 fixed in v1.7)
- [x] Iteration 8 complete (Codex REQUEST_CHANGES on v1.8 — all P2/P3 fixed in v1.8)
- [x] Iteration 9 complete (Codex REQUEST_CHANGES on v1.9 — all P2/P3 fixed in v1.9)
- [x] Iteration 10 complete (Codex REQUEST_CHANGES on v1.10 — all P2/P3 fixed in v1.10)
- [x] Iteration 11 complete (Codex REQUEST_CHANGES on v1.11 — all P2/P3 fixed in v1.11)
- [x] Iteration 12 complete (Codex REQUEST_CHANGES on v1.12 — all P1/P2/P3 fixed in v1.12)
- [x] Iteration 13 complete (Codex REQUEST_CHANGES on v1.13 — all P2/P3 fixed in v1.13)
- [x] **Iteration 14**: Codex **APPROVE** on v1.13 — spec approved for implementation ✅

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
│   ├── model_overview.py
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
├── report_generator.py               # generate_orcaflex_report(data, output_path, include_plotlyjs="cdn")
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

**Pass/fail precedence rule**: `UtilizationData.pass_fail: Optional[bool] = None` (per-check field; `DesignCheckData` is the container with no `pass_fail` of its own). Normalized value = `pass_fail if pass_fail is not None else (uc <= 1.0)`. If provided and contradicts derived value, keep provided value and render `⚠️ CONFLICT` badge. Executive verdict = `all(normalized_pass_fail(c) for c in checks) if checks else None`. Empty `checks` list → render `⚠️ NO CHECKS` in executive summary (neither PASS nor FAIL).

**Dependency versions (resolved)**:

| Package | Version constraint | Notes |
|---|---|---|
| `pydantic` | `>=2.5` | v2 field validators, `model_validate()` |
| `plotly` | `>=6.1.1` | CDN compatibility (Plotly 6.x CDN URL scheme); WRK-129 is HTML-only output, no `write_image()` in scope |
| `OrcFxAPI` | any licensed | Extractors only; data models are OrcFxAPI-free |
| `playwright` | `>=1.40` | Acceptance tests only; optional dev dependency |

### Top-Level API

```python
from digitalmodel.solvers.orcaflex.reporting import generate_orcaflex_report
from digitalmodel.solvers.orcaflex.reporting.models.report import OrcaFlexAnalysisReport
from digitalmodel.solvers.orcaflex.reporting.models.geometry import GeometryData, KeyPointData

# Populate data model (canonical field names for OrcaFlexAnalysisReport)
report_data = OrcaFlexAnalysisReport(
    project_name="GoM SCR Design Study",
    structure_id="SCR-001",
    structure_type="riser",
    design_codes=["DNV-OS-F201", "DNV-RP-C203"],
    geometry=GeometryData(...),
    materials=MaterialData(...),
    boundary_conditions=BCData(...),
    mesh=MeshData(...),
    loads=[LoadCaseData(...)],         # field: loads — list of load cases
    static_results=StaticResultsData(...),
    dynamic_results=DynamicResultsData(...),
    extreme_results=ExtremeResultsData(...),
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
- [ ] `UtilizationData` — per-check: `name: str`, `value: float`, `allowable: float`, `uc: float`, `pass_fail: Optional[bool] = None`; derive `uc <= 1.0` when `None`; show `⚠️ CONFLICT` badge when provided value contradicts derived value
- [ ] `DesignCheckData` — container: `code: str`, `checks: list[UtilizationData]`; `pass_fail` lives on `UtilizationData` only
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

> **Mandatory-section placeholder ownership**: Section builders are "dumb" — they return `""` when `data=None` for both mandatory and conditional sections. `report_generator.py` owns placeholder injection: for every mandatory section (per Anchor Contract table), if the builder returns `""`, the generator wraps the anchor in the empty-state template (`<section id="{anchor}"><div class="section-card section-empty">…</div></section>`). Conditional sections remain absent when builder returns `""`.

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
- [ ] `generate_orcaflex_report(data, output_path, include_plotlyjs="cdn")` — entry point; `structure_type` is read from `data.structure_type` (not a separate parameter)
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
│                                #   + HTML-escape (6 tests): project_name, structure_id, analyst,
│                                #     load-case label, UtilizationData.name, recommendation text
│                                #     — each: <script>alert(1)</script> → &lt;script&gt;...&lt;/script&gt;
│                                #   + Global XSS test (1 test): inject payload into EXACTLY:
│                                #     project_name, structure_id, analyst, design_codes[0],
│                                #     LoadCaseData.id, UtilizationData.name, summary.recommendations[0]
│                                #     — assert raw literal "<script>alert(1)</script>" not in html
├── test_renderers.py            # Each renderer produces section sequence with required anchors
└── test_report_generator.py     # End-to-end: fixture data → HTML file
                                 #   + html.parser parses without error
                                 #   + all expected anchor IDs present
                                 #   + Plotly divs present ONLY in sections marked
                                 #     Has Plot(s)? = Yes in the Anchor Contract table
                                 #     (header, model-overview, analysis-setup, summary,
                                 #      appendices must NOT contain chart divs)
```

### Negative-Path Tests (required)
```
test_models.py:
  - OrcaFlexAnalysisReport with only project_name set (all sections None) → valid model
  - UtilizationData(uc=1.05, pass_fail=None) → normalized pass_fail = False (derived: uc <= 1.0 = False)
  - DesignCheckData is a container only — instantiation without pass_fail is valid
  - DesignCheckData(code="DNV", checks=[]) → executive_pass_fail returns None (empty → N/A, not PASS)
  - MeshData with empty segment list → MeshQualityData.verdict = "insufficient_data"

test_section_builders.py:
  - _build_geometry_html(None) → returns ""
  - _build_fatigue_html(None) → returns "" (conditional section)
  - _build_dynamic_results_html(data_with_empty_load_cases) → section renders with "no cases" notice

test_report_generator.py:
  - generate_orcaflex_report with no results populated → produces valid HTML (setup-only report)
  - generate_orcaflex_report with data.structure_type="invalid_type" → raises ValueError with clear message
  - Output path parent directory does not exist → directory created automatically
  - All section payloads None → every mandatory anchor ID still present in output HTML (placeholder rendered by generator)
  - CDN mode: output <script> src matches https://cdn.plot.ly/plotly-{version}.min.js (pinned)
  - CDN mode: output <script> tag contains integrity="sha384-..." and crossorigin="anonymous"
  - Offline mode (include_plotlyjs=True): output HTML contains embedded Plotly JS bundle
  - Offline mode: output HTML does NOT contain cdn.plot.ly in any <script src=...>
  - Global XSS test: inject "<script>alert(1)</script>" into the enumerated string fields (see
    HTML injection security block); verify the raw literal "<script>alert(1)</script>" does NOT
    appear anywhere in output HTML (the escaped form "&lt;script&gt;" may be present — that is
    correct; search for `"<script>alert(1)</script>" not in html`, NOT absence of all <script>)
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
- [ ] `generate_orcaflex_report(data, output_path)` produces a `.html` file at `output_path`; `structure_type` is read from `data.structure_type`
- [ ] Generated HTML is a single file: no sibling `.css`, `.js`, or image files required
- [ ] HTML passes `html.parser` parse without error (Python `html.parser.HTMLParser`); additionally: every mandatory section has `<section id="{anchor}">` directly containing `<div class="section-card">` or `<div class="section-card section-empty">` (structural assertion, not just anchor presence)
- [ ] Executive summary PASS/FAIL uses unified verdict rule:
  - `UtilizationData.pass_fail: Optional[bool]` (per-check, default `None`) is the single source of truth if provided by upstream module
  - If `pass_fail` is absent: derived as `pass_fail = (uc <= 1.0)`
  - If `pass_fail=True` but `uc > 1.0` (or vice versa): display both + `⚠️ CONFLICT` badge; `pass_fail` governs
  - Executive PASS = `all(normalized_pass_fail(c) for c in report.design_checks.checks) if report.design_checks.checks else None` — empty list → `None` (render `⚠️ NO CHECKS`, not PASS) where `normalized_pass_fail(c) = c.pass_fail if c.pass_fail is not None else (c.uc <= 1.0)`
- [ ] **Mandatory** sections with `None` data render a placeholder (`"No data available for this analysis"`) and are **never omitted** — the anchor `id` is always present in the HTML. **Conditional** sections are **fully omitted** (no DOM element, no placeholder) when their data field is `None`. The `Mandatory` / `Conditional` column in the Anchor Contract table is the single source of truth.
- [ ] CDN output (`include_plotlyjs="cdn"`): generated HTML `<script>` tag uses pinned version URL (`https://cdn.plot.ly/plotly-{installed_version}.min.js`), includes `integrity="sha384-{hash}"`, and `crossorigin="anonymous"` attributes
- [ ] Offline output (`include_plotlyjs=True`): generated HTML embeds Plotly JS bundle inline; output HTML must **not** contain any `<script src="https://cdn.plot.ly/...">` external CDN reference

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
- [ ] `UtilizationData` accepts: check name, value, allowable, UC float, `pass_fail: Optional[bool] = None` (per-check); `DesignCheckData` is the container (`code`, `checks: list[UtilizationData]`) with no `pass_fail` field of its own
- [ ] UC heatmap renders correctly for ≥ 2 checks × ≥ 5 arc-length positions
- [ ] PASS/FAIL status in executive summary follows the unified verdict rule: `pass_fail` field governs if provided; if absent → derived as `pass_fail = (uc <= 1.0)`; `⚠️ CONFLICT` badge shown if `pass_fail` and derived value disagree; `pass_fail` always wins

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
| Plotly CDN | `include_plotlyjs="cdn"` default, `True` for offline | CDN URL pinned to installed version with SRI integrity hash; offline option for air-gapped use |
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
| Review Iteration 4 | ✅ Complete | Codex REQUEST_CHANGES (v1.4 additions) — all P1/P2 fixed |
| Review Iteration 5 | ✅ Complete | Codex REQUEST_CHANGES (P1×2 dup anchor/pass_fail, P2×2 HTML-escape/wording) — all fixed in v1.5 |
| Review Iteration 6 | ✅ Complete | Codex REQUEST_CHANGES (P1×1 placeholder ownership, P2×2 field names/pass_fail expr) — all fixed in v1.6 |
| Review Iteration 7 | ✅ Complete | Codex REQUEST_CHANGES (P1×1 pass_fail ownership, P2×2 model_overview.py/HTML-escape breadth) — all fixed in v1.7 |
| Review Iteration 8 | ✅ Complete | Codex REQUEST_CHANGES (P2×2 loads list/CDN SRI in AC+tests; P3×1 pass_fail type) — all fixed in v1.8 |
| Review Iteration 9 | ✅ Complete | Codex REQUEST_CHANGES (P2×1 gate NO_OUTPUT policy, P3×1 DesignCheckData test bullet) — all fixed in v1.9 |
| Review Iteration 10 | ✅ Complete | Codex REQUEST_CHANGES (P2×1 Plotly div scope, P3×1 codex.feedback stale) — all fixed in v1.10 |
| Review Iteration 11 | ✅ Complete | Codex REQUEST_CHANGES (P2×1 universal escaping, P2×1 offline AC+tests, P3×1 gate ambiguity) — all fixed in v1.11 |
| Review Iteration 12 | ✅ Complete | Codex REQUEST_CHANGES (P1×1 global XSS re.search broken, P2×1 empty checks→PASS, P3×1 XSS field enum ambiguous) — all fixed in v1.12 |
| Review Iteration 13 | ✅ Complete | Codex REQUEST_CHANGES (P2×1 function signature, P2×1 escaping enforcement, P3×1 html.parser) — all fixed in v1.13 |
| Review Iteration 14 | ✅ **APPROVED** | Codex **APPROVE** on v1.13 — spec is ready for Phase 1 implementation |
| Plan Approved | ✅ **APPROVED** | Codex APPROVE iter 14 (v1.13) — cleared for implementation |
| Phase 1: Data Models + Implementation | ✅ Complete | 51 tests, 82.98% coverage, legal clean — commit e0df5acc |
| Phase 2a: Setup Section Builders | ✅ Complete | Section builders for geometry, materials, BC, mesh, loads |
| Phase 2b: Results Section Builders | ✅ Complete | Static, dynamic, extreme results + fatigue sections |
| Phase 3: Renderers + Report Generator | ✅ Complete | 5 renderers, generate_orcaflex_report(), 82.98% coverage |
| Phase 4: Pipeline Integration | ✅ Complete | 5 extractors, aggregator, --html-report CLI, 81.8% coverage — WRK-314 commit 591ec264 |

---

## HTML Section Inner Structure

### Section Card Template

Every section builder outputs this HTML skeleton. The `id` on `<section>` is the
mandatory anchor; `id` on each `<h3>` is the subsection anchor for deep-linking and
integration test assertions.

```html
<section id="{anchor}">
  <div class="section-card">
    <h2 class="section-title">{N}. {Title}</h2>
    <div class="section-body">
      <h3 id="{anchor}-{sub}">{Na}. {Subtitle}</h3>
      <div class="plotly-chart"><!-- fig.to_html(full_html=False) --></div>
      <!-- repeat for each subsection -->
    </div>
  </div>
</section>
```

Mandatory section with no data (placeholder — never omit the anchor):

```html
<section id="{anchor}">
  <div class="section-card section-empty">
    <h2 class="section-title">{N}. {Title}</h2>
    <p class="no-data">No data available for this analysis.</p>
  </div>
</section>
```

### Subsection Anchor Map

| Section Anchor | Subsection ID | h3 Label | Has Plot |
|---|---|---|---|
| `#executive-summary` | `#exec-uc-chart` | UC Summary Chart | Yes |
| `#executive-summary` | `#exec-verdict` | Verdict & Warnings | No |
| `#geometry` | `#geometry-3d` | 4a. 3D Line Profile | Yes |
| `#geometry` | `#geometry-2d` | 4b. 2D Vertical Profile | Yes |
| `#geometry` | `#geometry-plan` | 4c. Plan View | Yes |
| `#geometry` | `#geometry-key-points` | Key Points Table | No |
| `#materials` | `#materials-linetype-table` | Line Type Properties | No |
| `#materials` | `#materials-section-props` | 5a. Section Properties | Yes |
| `#materials` | `#materials-submerged-weight` | 5b. Submerged Weight Profile | Yes |
| `#boundary-conditions` | `#bc-annotation` | 6a. BC Annotation Overlay | Yes |
| `#boundary-conditions` | `#bc-seabed-reaction` | 6b. Seabed Reaction Profile | Yes |
| `#mesh` | `#mesh-segment-lengths` | 7a. Segment Length Profile | Yes |
| `#mesh` | `#mesh-adjacent-ratio` | 7b. Adjacent Ratio Profile | Yes |
| `#mesh` | `#mesh-quality-table` | 7c. Quality Table | No |
| `#other-structures` | `#other-struct-positions` | 8a. Attached Structure Positions | Yes |
| `#other-structures` | `#other-struct-buoyancy` | 8b. Buoyancy Profile | Yes |
| `#loads` | `#loads-current-profile` | 9a. Current Profile | Yes |
| `#loads` | `#loads-wave-scatter` | 9b. Wave Scatter Diagram | Yes |
| `#loads` | `#loads-case-table` | 9c. Load Case Matrix | No |
| `#static-results` | `#static-tension-profile` | 11a. Static Tension Profile | Yes |
| `#static-results` | `#static-bm-profile` | 11b. Static BM Profile | Yes |
| `#dynamic-results` | `#dynamic-te-history` | 12a. Tension Time History | Yes |
| `#dynamic-results` | `#dynamic-bm-history` | 12b. BM Time History | Yes |
| `#dynamic-results` | `#dynamic-te-envelope` | 12c. Tension Envelope | Yes |
| `#dynamic-results` | `#dynamic-bm-envelope` | 12d. BM Envelope | Yes |
| `#dynamic-results` | `#dynamic-stats-table` | 12f. Statistical Summary Table | No |
| `#extreme-results` | `#extreme-mpm-chart` | 13a. MPM Comparison | Yes |
| `#design-checks` | `#dc-heatmap` | 14a. UC Heatmap | Yes |
| `#design-checks` | `#dc-summary-table` | 14b. Summary Table | No |
| `#fatigue` | `#fatigue-damage-profile` | 15a. Damage Profile | Yes |
| `#fatigue` | `#fatigue-life-profile` | 15b. Life Profile (log y) | Yes |
| `#fatigue` | `#fatigue-rainflow` | 15c. Rainflow Matrix | Yes |

**Structure-type-specific subsections** (injected by renderer, not base builder):

> **Ownership rule**: Base builder `_build_dynamic_results_html()` produces subsections 12a–12d and 12f only. `#dynamic-tdp-excursion` (12e) is injected exclusively by `RiserRenderer` — it must NOT appear in base builder output. This avoids duplicate `id` attributes in riser reports.

| Renderer | Subsection ID | h3 Label | Parent Section |
|---|---|---|---|
| `RiserRenderer` | `#dynamic-tdp-excursion` | TDP Excursion (12e) | `#dynamic-results` |
| `RiserRenderer` | `#dc-viv-susceptibility` | VIV Susceptibility | `#design-checks` |
| `PipelineRenderer` | `#geometry-kp-chainage` | KP Chainage Table | `#geometry` |
| `PipelineRenderer` | `#dc-upheaval` | Upheaval Buckling | `#design-checks` |
| `MooringRenderer` | `#geometry-spider` | Mooring Spread Diagram | `#geometry` |
| `MooringRenderer` | `#static-per-line-tensions` | Per-Line Tension Table | `#static-results` |
| `MooringRenderer` | `#static-offset-restoring` | Offset-Restoring Curve | `#static-results` |
| `JumperRenderer` | `#dynamic-end-rotations` | End Rotation Angles | `#dynamic-results` |
| `JumperRenderer` | `#dc-viv-vertical-legs` | VIV — Vertical Legs | `#design-checks` |
| `InstallationRenderer` | `#geometry-stinger` | Stinger Configuration | `#geometry` |
| `InstallationRenderer` | `#dc-overbend` | Overbend Curvature | `#design-checks` |
| `InstallationRenderer` | `#dc-departure-angle` | Departure Angle | `#design-checks` |

---

## Fast OrcFxAPI Extraction Patterns

Phase 4 extractors must use vectorised API calls. Loop-per-node patterns are
~100× slower and unacceptable in production.

### Profile statistics: `RangeGraph` without `objectExtra`

```python
# SLOW — O(n_nodes) round-trips
te_max = [
    line.RangeGraph("Effective Tension", ofx.pnDynamic,
                    objectExtra=ofx.oeArcLength(s)).Max
    for s in arc_lengths
]

# FAST — one call, returns arrays over all range graph positions
rg = line.RangeGraph("Effective Tension", ofx.pnDynamic)
te_max  = list(rg.Max)   # shape (n_range_graph_positions,)
te_min  = list(rg.Min)
te_mean = list(rg.Mean)
```

> **Prerequisite**: the OrcaFlex model must have range graph output requested for
> the relevant variables (General > Outputs > Range Graphs). The positions returned
> match `line.NodeArclengths` only when range graphs are set to "all nodes".

### Governing location first — time series second

```python
rg_te = line.RangeGraph("Effective Tension", ofx.pnDynamic)
governing_idx = int(np.argmax(rg_te.Max))
governing_s   = arc_lengths[governing_idx]          # scalar [m]

# Extract time history only at the governing location (one call)
te_ts = list(line.TimeHistory(
    "Effective Tension", ofx.pnDynamic,
    objectExtra=ofx.oeArcLength(governing_s),
))
```

### Reuse the model object across simulation files

```python
model = ofx.Model()                                 # single license checkout

results = {}
for case_id, sim_path in load_cases.items():
    model.LoadSimulation(str(sim_path))             # swap results, keep license
    rg = model["SCR-001"].RangeGraph("Effective Tension", ofx.pnDynamic)
    results[case_id] = {"te_max": list(rg.Max), "te_min": list(rg.Min)}
```

### Arc-length array

```python
arc_lengths = list(model["SCR-001"].NodeArclengths)
# Index 0 = End A (0.0 m); last = total unstretched length
```

### Static shape (no vectorised API — but negligible cost)

```python
# StaticResult has no vectorised form; loop is acceptable (no time-domain data)
x_s = [line.StaticResult("X", ofx.oeArcLength(s)) for s in arc_lengths]
z_s = [line.StaticResult("Z", ofx.oeArcLength(s)) for s in arc_lengths]
```

---

## Worked Examples by Structure Type

One fixture per structure type. Fixtures serve as:
- Integration test inputs (`tests/solvers/orcaflex/reporting/fixtures/`)
- Golden HTML baselines (`docs/modules/orcaflex/reporting/examples/`)
- Developer reference for data model field mapping

---

### Example 1: GoM SCR Riser (SCR-001)

**Parameters**:

| Property | Value |
|---|---|
| Structure type | Steel Catenary Riser (SCR) |
| Water depth | 1500 m |
| Pipe OD × WT | 323.9 mm × 25.4 mm (12.75" NPS) |
| Grade | X65, SMYS = 448 MPa |
| Riser length | ~2100 m |
| Configuration | Simple catenary, no buoyancy aids |
| Governing check | Fatigue (UC = 0.95 at TDP) |
| Design codes | DNV-OS-F201, DNV-RP-C203 |
| OrcaFlex line name | `"SCR-001"` |

**Key points**:

| Label | Arc length (m) | x (m) | z (m) |
|---|---|---|---|
| Hang-off (End A) | 0.0 | 0.0 | −20.0 |
| Sag-bend | 820.0 | 610.0 | −680.0 |
| TDP (static) | 1960.0 | 1210.0 | −1500.0 |

**Renderer**: `RiserRenderer`

**OrcFxAPI → data model mapping**:

```python
import numpy as np
import OrcFxAPI as ofx
from digitalmodel.solvers.orcaflex.reporting.models.report import OrcaFlexAnalysisReport
from digitalmodel.solvers.orcaflex.reporting.models.geometry import (
    GeometryData, LineProfileData, KeyPointData,
)
from digitalmodel.solvers.orcaflex.reporting.models.materials import (
    MaterialData, LineTypeData,
)
from digitalmodel.solvers.orcaflex.reporting.models.mesh import (
    MeshData, SegmentData, MeshQualityData,
)
from digitalmodel.solvers.orcaflex.reporting.models.results import (
    DynamicResultsData, TimeSeriesData, EnvelopeData,
)
from digitalmodel.solvers.orcaflex.reporting.models.design_checks import (
    DesignCheckData, UtilizationData,
)
from digitalmodel.solvers.orcaflex.reporting import generate_orcaflex_report

model = ofx.Model()
model.LoadSimulation("SCR-001_100yr_collinear.sim")
line = model["SCR-001"]
period = ofx.pnDynamic

# --- Geometry (fast static extraction) ---
arc_lengths = list(line.NodeArclengths)
x_s = [line.StaticResult("X", ofx.oeArcLength(s)) for s in arc_lengths]
z_s = [line.StaticResult("Z", ofx.oeArcLength(s)) for s in arc_lengths]
y_s = [0.0] * len(arc_lengths)

geometry = GeometryData(
    coordinate_system="MSL, z-positive-up",
    water_depth_m=1500.0,
    line_profile=LineProfileData(arc_length=arc_lengths, x=x_s, y=y_s, z=z_s),
    key_points=[
        KeyPointData(label="Hang-off",   arc_length_m=0.0,    x=0.0,    z=-20.0),
        KeyPointData(label="Sag-bend",   arc_length_m=820.0,  x=610.0,  z=-680.0),
        KeyPointData(label="TDP static", arc_length_m=1960.0, x=1210.0, z=-1500.0),
    ],
    hang_off_angle_deg=15.2,
    tdp_excursion_near_m=1185.0,
    tdp_excursion_far_m=1240.0,
)

# --- Mesh (fast RangeGraph-less; segment properties from model) ---
segs = line.NumberOfSegments
seg_lengths = [line.SegmentLength[i] for i in range(segs)]
adj_ratios = [
    max(seg_lengths[i], seg_lengths[i + 1]) / min(seg_lengths[i], seg_lengths[i + 1])
    for i in range(segs - 1)
]
worst_idx = int(np.argmax(adj_ratios))
arc_lens_seg = [sum(seg_lengths[:i]) for i in range(segs)]

mesh = MeshData(
    total_segment_count=segs,
    segments=[SegmentData(arc_length_m=arc_lens_seg[i], length_m=seg_lengths[i])
              for i in range(segs)],
    quality=MeshQualityData(
        max_adjacent_ratio=adj_ratios[worst_idx],
        worst_ratio_arc_length_m=arc_lens_seg[worst_idx],
        verdict="PASS" if adj_ratios[worst_idx] < 3.0 else "WARNING",
        adjacent_ratios=adj_ratios,
    ),
)

# --- Dynamic results (vectorised envelope + single governing time series) ---
rg_te = line.RangeGraph("Effective Tension", period)   # one call — all nodes
te_max = list(rg_te.Max)
te_min = list(rg_te.Min)
governing_s = arc_lengths[int(np.argmax(te_max))]      # worst Te arc length

times  = list(model.SampleTimes(period))
te_ts  = list(line.TimeHistory("Effective Tension", period,
               objectExtra=ofx.oeArcLength(governing_s)))
bm_ts  = list(line.TimeHistory("Bend Moment", period,
               objectExtra=ofx.oeArcLength(governing_s)))
tdp_ts = list(line.TimeHistory("X", period,
               objectExtra=ofx.oeArcLength(1960.0)))    # TDP x-excursion

dynamic = DynamicResultsData(
    ramp_end_time_s=200.0,
    time_series=[
        TimeSeriesData(id="te_governing",  label=f"Te @ {governing_s:.0f}m",
                       t=times, values=te_ts,  units="kN"),
        TimeSeriesData(id="bm_governing",  label=f"BM @ {governing_s:.0f}m",
                       t=times, values=bm_ts,  units="kN·m"),
        TimeSeriesData(id="tdp_excursion", label="TDP x-position",
                       t=times, values=tdp_ts, units="m"),
    ],
    envelopes=[
        EnvelopeData(id="te_envelope", label="Effective Tension Envelope",
                     arc_length=arc_lengths,
                     max_values=te_max, min_values=te_min, units="kN"),
    ],
)

# --- Design checks (pre-computed) ---
checks = DesignCheckData(
    code="DNV-OS-F201 (2010) + DNV-RP-C203 (2016)",
    checks=[
        UtilizationData(name="Combined Loading §5.4.2.2",
                        value=0.82, allowable=1.0, uc=0.82, pass_fail=True,
                        location_arc_m=820.0, load_case="100yr_collinear"),
        UtilizationData(name="Fatigue damage (F3 weld)",
                        value=0.031, allowable=0.033, uc=0.95, pass_fail=True,
                        location_arc_m=1960.0, load_case="fatigue_scatter"),
        UtilizationData(name="Burst pressure §5.4.2.1",
                        value=28.4, allowable=35.2, uc=0.81, pass_fail=True,
                        location_arc_m=1500.0, load_case="100yr_collinear"),
    ],
)

report_data = OrcaFlexAnalysisReport(
    project_name="GoM SCR Design Study",
    structure_id="SCR-001",
    structure_type="riser",
    analyst="J. Smith",
    orcaflex_version="11.4",
    design_codes=["DNV-OS-F201", "DNV-RP-C203"],
    geometry=geometry,
    mesh=mesh,
    dynamic_results=dynamic,
    design_checks=checks,
)

generate_orcaflex_report(
    report_data,
    output_path="docs/modules/orcaflex/reporting/examples/SCR-001_report.html",
    include_plotlyjs="cdn",
)
```

**Design checks**:

| Check | UC | Status |
|---|---|---|
| Combined loading (§5.4.2.2) | 0.82 | ✅ PASS |
| Fatigue damage — F3 weld | 0.95 | ✅ PASS |
| Burst pressure (§5.4.2.1) | 0.81 | ✅ PASS |

---

### Example 2: Deepwater Pipeline (PIPE-FL-001)

**Parameters**:

| Property | Value |
|---|---|
| Structure type | Subsea Pipeline |
| Water depth | 800 m (variable seabed) |
| Pipe OD × WT | 406.4 mm × 20.6 mm (16" NPS) |
| Grade | X65 |
| Modelled length | 500 m section spanning free-span |
| Free-span | KP 6200–6500 m, 3.5 m gap |
| Governing check | Combined loading at free-span mid (UC = 0.87) |
| Design codes | DNV-OS-F101, DNV-RP-F105 |
| OrcaFlex line name | `"Pipeline"` |

**Key points**:

| Label | KP (m) | z (m) |
|---|---|---|
| Tie-in — End A | 0.0 | −800.0 |
| Free-span start | 6200.0 | −798.0 |
| Free-span midpoint | 6350.0 | −793.0 (3.5 m gap) |
| Free-span end | 6500.0 | −798.0 |
| Tie-in — End B | 12000.0 | −795.0 |

**Renderer**: `PipelineRenderer` — adds `#geometry-kp-chainage`, `#dc-upheaval`

**Pipeline-specific fields populated**:
- `GeometryData.kp_chainage_table` — KP, easting, northing, water depth per KP
- `GeometryData.inline_fittings = [{"label": "PLET-A", "kp_m": 0.0}]`
- `GeometryData.seabed_profile` — arc length vs seabed z (from survey data)
- `LoadCaseData.thermal_delta_t_c = 60.0`
- `LoadCaseData.internal_pressure_mpa = 18.5`
- `LoadCaseData.content_density_kg_m3 = 850.0`

**Fast extraction note**: For pipelines, `RangeGraph` on `"Effective Tension"` and
`"Bend Moment"` gives the free-span UC governing location in one call each —
no need to iterate along KP.

**Design checks**:

| Check | UC | Status |
|---|---|---|
| Combined loading — free-span (DNV-OS-F101 §5.4.6) | 0.87 | ✅ PASS |
| VIV onset — free-span (DNV-RP-F105) | 0.62 | ✅ PASS |
| Upheaval buckling (DNV-RP-F110) | 0.43 | ✅ PASS |
| Burst pressure | 0.76 | ✅ PASS |

---

### Example 3: Rigid Jumper (JMP-A-001)

**Parameters**:

| Property | Value |
|---|---|
| Structure type | Rigid Jumper (M-shape) |
| Water depth | 600 m |
| Pipe OD × WT | 168.3 mm × 14.3 mm (6" NPS) |
| Grade | X65 with CRA liner |
| Span length | 28 m (PLET to PLEM) |
| Arch height | 8 m above seabed |
| Governing check | Flex joint end rotation (UC = 0.87) |
| Design codes | ASME B31.8, DNV-RP-F116 |
| OrcaFlex line name | `"Jumper"` |

**Key points**:

| Label | Arc length (m) | z (m) |
|---|---|---|
| PLET flange (End A) | 0.0 | −600.0 |
| Arch crest | 14.2 | −592.0 |
| PLEM flange (End B) | 29.6 | −600.0 |

**Renderer**: `JumperRenderer` — adds `#dynamic-end-rotations`, `#dc-viv-vertical-legs`

**Jumper-specific fields populated**:
- `GeometryData.span_length_m = 28.0`
- `GeometryData.arch_height_m = 8.0`
- `GeometryData.offset_angle_deg = 22.5`
- `BCData.end_a.flex_joint_stiffness_knm_per_deg = 12.5`
- `BCData.relative_displacement_m` — PLET/PLEM relative motion from vessel motions
- `DynamicResultsData.end_rotation_ts` — flex joint angle time history

**Fast extraction note**: Jumpers are short (~30 m, ~50 segments). A
`RangeGraph` call returns the peak stress/curvature location immediately;
one `TimeHistory` at that location suffices. No per-node loops needed.

**Design checks**:

| Check | UC | Status |
|---|---|---|
| End rotation — End A flex joint | 0.87 | ✅ PASS |
| Combined stress at arch crest (ASME B31.8) | 0.71 | ✅ PASS |
| VIV susceptibility — vertical legs (DNV-RP-F105) | 0.33 | ✅ PASS |

---

### Example 4: Spread Mooring (FPSO-MOOR-001)

**Parameters**:

| Property | Value |
|---|---|
| Structure type | Spread Mooring System |
| Water depth | 390 m |
| Number of lines | 12 (3 groups × 4 lines) |
| Line composition | 76 mm stud-chain / 120 mm spiral-strand wire / 76 mm stud-chain |
| Vessel displacement | 80,000 DWT FPSO |
| Governing check | Intact max tension — Line 3 (UC = 0.78 intact; 0.91 one-line-damaged) |
| Design codes | API RP 2SK, DNV-OS-E301 |
| OrcaFlex line names | `"Mooring Line 1"` … `"Mooring Line 12"` |

**Key geometry (per line)**:

| Label | Value |
|---|---|
| Fairlead depth | −28.0 m (keel) |
| Nominal anchor radius | 1200 m |
| Static pretension range | 1850–2200 kN per line |

**Renderer**: `MooringRenderer` — adds `#geometry-spider`, `#static-per-line-tensions`,
`#static-offset-restoring`

**Mooring-specific fields populated**:
- `GeometryData.mooring_lines` — list of `MooringLineGeometry` per line (fairlead pos,
  anchor pos, arc length, line ID)
- `StaticResultsData.per_line_tensions` — pretension per line (intact + one-damaged)
- `DynamicResultsData.per_line_max_tensions` — dict[case_id → list[tension per line]]

**Fast extraction pattern** — all 12 lines in one loop:

```python
model = ofx.Model()
model.LoadSimulation("FPSO_MOOR_100yr_intact.sim")

per_line_max = {}
for i in range(1, 13):
    line = model[f"Mooring Line {i}"]
    rg = line.RangeGraph("Effective Tension", ofx.pnDynamic)
    per_line_max[f"Line {i}"] = float(max(rg.Max))   # scalar max over all nodes
```

**Design checks**:

| Check | Line | UC (intact) | UC (1-damaged) | Status |
|---|---|---|---|---|
| Max tension vs MBL × SF | Line 3 | 0.78 | 0.91 | ✅ PASS |
| Vessel offset (100yr) | — | 0.65 | 0.82 | ✅ PASS |

---

### Example 5: S-lay Installation (LAY-OP-001)

**Parameters**:

| Property | Value |
|---|---|
| Structure type | S-lay Pipeline Installation |
| Water depth | 250 m |
| Pipe OD × WT | 457.2 mm × 19.1 mm (18" NPS) |
| Grade | X65 |
| Stinger | Articulated, 90 m, 3 sections, 8 rollers |
| Governing check | Sagbend curvature (UC = 0.88) |
| Design codes | DNV-OS-F101 §5.4.7 |
| OrcaFlex line name | `"Pipeline"` |

**Key points**:

| Label | Arc length (m) | z (m) |
|---|---|---|
| Tensioner exit | 0.0 | 0.0 |
| Stinger tip | 92.0 | −55.0 |
| Inflection point | 280.0 | −130.0 |
| Sagbend | 450.0 | −220.0 |
| First seabed contact | 580.0 | −250.0 |

**Renderer**: `InstallationRenderer` — adds `#geometry-stinger`, `#dc-overbend`,
`#dc-departure-angle`

**Installation-specific fields populated**:
- `GeometryData.stinger_roller_positions` — list of `(arc_length_m, x, z)` per roller
- `GeometryData.departure_angle_deg = 6.8`
- `GeometryData.layback_m = 580.0`
- `LoadCaseData.tensioner_load_kn = 850.0`
- `LoadCaseData.backstroke_m = 0.8`
- `DynamicResultsData.overbend_curvature_ts` — stinger region curvature time history
- `DynamicResultsData.sagbend_curvature_ts` — sagbend curvature time history

**Fast extraction note**: Installation analysis typically has a small number of
`"Wave Response"` or irregular wave load cases. Use `model.LoadSimulation()` in
a loop. Extract `RangeGraph("Curvature")` for both stinger and sagbend regions;
the `RangeGraph` call is already vectorised along the full pipeline length.

**Design checks**:

| Check | UC | Status |
|---|---|---|
| Overbend strain (§5.4.7) | 0.72 | ✅ PASS |
| Sagbend curvature | 0.88 | ✅ PASS |
| Dynamic tension variation (tensioner) | 0.61 | ✅ PASS |

---

## Session Log

| Date | Session ID | Agent | Notes |
|------|------------|-------|-------|
| 2026-02-17 | 2026-02-17-wrk-129 | claude-sonnet-4-6 | Plan created — FEA causal chain layout, FE analyst skill companion |
| 2026-02-18 | 2026-02-18-wrk-129 | claude-sonnet-4-6 | Cross-review complete (3 Codex iterations). v1.3 approved. |
| 2026-02-21 | 2026-02-21-wrk-129 | claude-sonnet-4-6 | Added HTML inner structure (subsection anchor map), fast OrcFxAPI extraction patterns, and worked examples for all 5 structure types. |
| 2026-02-23 | 2026-02-23-wrk-129 | claude-sonnet-4-6 | Cross-review iter 4: Codex REQUEST_CHANGES (P1×1 exec PASS/FAIL, P2×3 dup version/stale table/CDN security). Fixed all P1/P2 in v1.4. |
| 2026-02-23 | 2026-02-23-wrk-129-b | claude-sonnet-4-6 | Cross-review iter 5: Codex REQUEST_CHANGES (P1×2 dup anchor/pass_fail Optional, P2×2 HTML-escape/wording, P3×1 plotly). Fixed all in v1.5. |
| 2026-02-23 | 2026-02-23-wrk-129-c | claude-sonnet-4-6 | Cross-review iter 6: Codex REQUEST_CHANGES (P1×1 placeholder ownership, P2×2 field names/pass_fail expr). Fixed all in v1.6. |
| 2026-02-23 | 2026-02-23-wrk-129-d | claude-sonnet-4-6 | Cross-review iter 7: Codex REQUEST_CHANGES (P1×1 pass_fail ownership UtilizationData vs DesignCheckData, P2×2 model_overview.py missing/HTML-escape breadth). Fixed all in v1.7. |
| 2026-02-23 | 2026-02-23-wrk-129-e | claude-sonnet-4-6 | Cross-review iter 8: Codex REQUEST_CHANGES (P2×2 loads list/CDN SRI not in AC+tests; P3×1 pass_fail type). Fixed all in v1.8. |
| 2026-02-23 | 2026-02-23-wrk-129-f | claude-sonnet-4-6 | Cross-review iter 9: Codex REQUEST_CHANGES (P2×1 gate NO_OUTPUT policy; P3×1 DesignCheckData test bullet wrong class). Fixed all in v1.9. |
| 2026-02-23 | 2026-02-23-wrk-129-g | claude-sonnet-4-6 | Cross-review iter 10: Codex REQUEST_CHANGES (P2×1 Plotly div scope all-vs-plot-only; P3×1 codex.feedback stale). Fixed all in v1.10. |
| 2026-02-23 | 2026-02-23-wrk-129-h | claude-sonnet-4-6 | Cross-review iter 11: Codex REQUEST_CHANGES (P2×1 universal escaping via _escape() helper + global XSS test; P2×1 offline mode AC+tests; P3×1 gate ambiguity). Fixed all in v1.11. |
| 2026-02-23 | 2026-02-23-wrk-129-i | claude-sonnet-4-6 | Cross-review iter 12: Codex REQUEST_CHANGES (P1×1 global XSS re.search broken; P2×1 empty checks→PASS not N/A; P3×1 XSS field enum ambiguous). Fixed all in v1.12. |
| 2026-02-23 | 2026-02-23-wrk-129-j | claude-sonnet-4-6 | Cross-review iter 13: Codex REQUEST_CHANGES (P2×1 generate_orcaflex_report signature inconsistent; P2×1 escaping enforcement rule; P3×1 html.parser weak). Fixed all in v1.13. |
| 2026-02-23 | 2026-02-23-wrk-129-k | claude-sonnet-4-6 | Cross-review iter 14: Codex **APPROVE** on v1.13. Spec cleared for Phase 1 implementation. Legal sanity scan pending. |
