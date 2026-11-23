# Workspace Hub — Roadmap

## Milestones

- ✅ **v1.0 Foundation Sprint** — Phases 1-6 (shipped 2026-03-30) — [archive](milestones/v1.0-ROADMAP.md)

## Phases

<details>
<summary>✅ v1.0 Foundation Sprint (Phases 1-6) — SHIPPED 2026-03-30</summary>

- [x] Phase 1: Accelerate digitalmodel development (5/5 plans) — completed 2026-03-25
- [x] Phase 2: Accelerate worldenergydata pipelines (6/6 plans) — completed 2026-03-26
- [x] Phase 3: GTM and marketing — aceengineer-website (3/3 plans) — completed 2026-03-27
- [x] Phase 4: Client acquisition (3/3 plans) — completed 2026-03-28
- [x] Phase 5: Nightly research automation (2/2 plans) — completed 2026-03-28
- [x] Phase 6: Update plan and vision for digitalmodel repo (2/2 plans) — completed 2026-03-29

</details>

### Phase 7: Solver Verification Gate — OrcFxAPI + remote execution go/no-go [H1]

**Goal:** Verify OrcFxAPI loads/solves/exports on licensed-win-1, establish remote Claude Code execution from dev-primary, and enforce solver/non-solver module separation in codebase
**Depends on:** Phase 1 (digitalmodel acceleration)
**Requirements:** [INFRA-01, INFRA-02]
**Context:** Go/no-go gate for v1.1 OrcaWave Automation milestone. Three verification pillars: (1) OrcFxAPI functional on licensed-win-1, (2) remote CC trigger from dev-primary, (3) clean solver/non-solver module boundary.
**Plans:** 3 plans

Plans:
- [x] 07-01-PLAN.md — Module boundary refactoring + test infrastructure (solver/ subpackage, pytest markers)
- [x] 07-02-PLAN.md — Licensed-win-1 infrastructure verification (SSH, OrcFxAPI, Claude Code, uv)
- [ ] 07-03-PLAN.md — Smoke test execution (L00+L01) + artifact commit

## Backlog

### Phase 999.1: Ship Plan CAD Pipeline — Curve reconstruction for 3D hull lofting (BACKLOG)
<!-- H2: geometry reconstruction for autonomous hull lofting -->
<!-- WRK rubric: 1/4 (no named gap, no autonomy lift, no SPA loop, no time-to-result) -->

**Goal:** Reconstruct continuous hull curves from fragmented skeleton vectorization, enabling 3D hull surface generation via FreeCAD/Gmsh
**Context:** WRK-5055 Phase 1 complete — 110 SNAME ship plans cataloged, 986 pages scanned, skeleton DXFs generated for all profiles and 3 lines plans (BB-45 USS Colorado, EC2-S-C1 Liberty Ship, SS-563 USS Tang). FreeCAD `Part.makeLoft()` proven functional but current vectorization produces fragmented pixel-edge traces unsuitable for direct lofting.
**Requirements:**
- Region segmentation: separate body plan / half-breadth / sheer plan views by pixel position
- Curve reconstruction: join fragments via directional continuity into continuous B-splines
- Curve classification: distinguish cross-sections from waterlines / buttocks / grid / text
- Coordinate transform: pixel space -> real units using known ship dimensions
- 3D placement: position cross-sections at longitudinal stations
- Install FreeCAD Ship Workbench addon (or upgrade to FreeCAD 1.0+)
**Consider:** geomdl/NURBS-Python for pure-Python curve fitting, Gmsh `addThruSections` for direct hull surface lofting
**Prerequisites:** ship-plans-catalog.yaml (110 vessels), skeleton DXFs for 3 lines plans, FreeCAD loft API proven
**Plans:** 0 plans

Plans:
- [ ] TBD (promote with $gsd-review-backlog when ready)

### Phase 999.2: Wind Energy, Turbines & Fitness-for-Service Vision (BACKLOG)
<!-- H2: new engineering domain expansion -->
<!-- WRK rubric: 1/4 (no named gap, potential L2→L3 for new domain, no SPA, no time-to-result) -->

**Goal:** Add calculation modules for wind/turbine structures and fitness-for-service assessments, targeting marine structures and ships first, then extending to wind energy and structural integrity assessment
**Context:** Extends digitalmodel's engineering domain beyond current offshore/subsea focus. Fitness-for-service (API 579-1/ASME FFS-1) is a natural complement to existing wall thickness and fatigue modules. Wind turbine foundation analysis (monopiles, jackets) overlaps with existing DNV expertise.
**Requirements:**
- Fitness-for-service assessment modules (API 579-1/ASME FFS-1): crack-like flaws, metal loss, creep damage
- Marine structure/ship structural assessment as first priority
- Wind turbine foundation analysis: monopile, jacket, gravity-based
- Turbine tower fatigue and buckling checks per relevant standards (DNV-ST-0126, IEC 61400)
- Integration with existing digitalmodel calculation framework and standards traceability manifests
**Consider:** Phased rollout — marine FFS first, then wind/turbine as separate sub-phases
**Prerequisites:** digitalmodel Phase 6 vision complete, existing fatigue and wall thickness modules as foundation
**Plans:** 0 plans

Plans:
- [ ] TBD (promote with $gsd-review-backlog when ready)

### Phase 999.3: CAD/CAM & Manufacturing Vision (BACKLOG)
<!-- H2: calculation-to-fabrication pipeline -->
<!-- WRK rubric: 0/4 (no named gap, no autonomy lift, no SPA, no time-to-result) -->

**Goal:** Define and implement CAD/CAM and manufacturing capabilities — bridging engineering calculations to fabrication-ready outputs
**Context:** Complements existing CAD-DEVELOPMENTS repo and OGManufacturing package. The ship plan CAD pipeline (999.1) demonstrates the need for geometry-to-manufacturing workflows. digitalmodel calculations currently stop at analysis results — this phase extends through to fabrication outputs.
**Requirements:**
- CAD model generation from calculation outputs (e.g., wall thickness -> pipe specification -> 3D model)
- Manufacturing-aware design checks (weldability, material availability, fabrication tolerances)
- Integration with FreeCAD for parametric modeling and drawing generation
- Bill of materials (BOM) generation from design specifications
- DXF/STEP/IGES export for shop floor consumption
**Consider:** FreeCAD Python API for parametric modeling, OGManufacturing package as foundation, link to ship plan pipeline (999.1) for hull manufacturing
**Prerequisites:** digitalmodel Phase 6 vision, CAD-DEVELOPMENTS repo audit, OGManufacturing package assessment
**Plans:** 0 plans

Plans:
- [ ] TBD (promote with $gsd-review-backlog when ready)

### Phase 999.4: Extend Autoresearch to Agent & Template Definitions (BACKLOG)
<!-- H1: AI interface skills for P1/P2 tools -->
<!-- WRK rubric: 3/4 (closes self-healing gap, L3→L4 lift, tightens SPA, reduces time-to-result) -->

**Goal:** Generalize the skill-autoresearch loop to iterate on agent definitions, research templates, and workflow configs — not just skills
**Context:** Current `skill-autoresearch-nightly.sh` only targets `.claude/skills/` files. The same accept/reject-on-metric pattern (inspired by karpathy/autoresearch) applies to agent prompts in `.claude/agents/`, research templates in `.claude/get-shit-done/templates/`, and planning configs. Each target type needs its own eval function (agent eval, template coverage check, etc.).
**Requirements:**
- Abstract the autoresearch loop into a generic runner that accepts a target type + eval function
- Add agent definition evaluation (clarity, tool usage accuracy, output quality scoring)
- Add template evaluation (section completeness, example quality)
- Results tracked per-target-type in `.claude/state/skill-autoresearch/`
- Same safety model: branch isolation, never auto-merge, human reviews next morning
**Consider:** Start with agents (highest leverage), then templates. Reuse existing `results.tsv` schema with a `target_type` column.
**Prerequisites:** Stable agent eval criteria, current skill-autoresearch proven reliable over 2+ weeks
**Plans:** 0 plans

Plans:
- [ ] TBD (promote with $gsd-review-backlog when ready)

### Phase 999.5: High-Iteration Autoresearch with Compounding Improvements (BACKLOG)
<!-- H1: compounding improvement loop -->
<!-- WRK rubric: 4/4 (closes self-healing gap, L3→L4 lift, tightens SPA, reduces time-to-result) -->

**Goal:** Increase autoresearch iteration depth from single-pass to multi-cycle per target per night (~10-12 iterations/target), enabling compounding improvements
**Context:** karpathy/autoresearch runs ~12 experiments/hour (~100 overnight). Our current loop does one pass per skill. With a 180s budget per iteration, we could fit ~10 iterations per skill per night within API budget constraints. Key insight: improvements compound — iteration N builds on accepted changes from iteration N-1.
**Requirements:**
- Configurable iteration count per target (default 5, max 12)
- Sequential accept/reject within a single target: accepted changes carry forward, rejected changes revert
- Budget guard: configurable max API spend per night, abort when reached
- Diminishing returns detection: stop early if 3 consecutive iterations show no improvement
- Summary report: iterations run, accepted/rejected counts, cumulative improvement per target
**Consider:** Start conservative (3 iterations) and increase as cost/quality tradeoffs become clear. Track cost-per-improvement to find the sweet spot.
**Prerequisites:** Phase 999.4 (generic autoresearch runner), 30-day baseline of single-pass results to measure compounding benefit
**Plans:** 0 plans

Plans:
- [ ] TBD (promote with $gsd-review-backlog when ready)

### Pint Unit Conversion Retrofit (BACKLOG)
<!-- H1: technical debt closure -->

**Goal:** Replace all hardcoded unit conversion factors in `src/digitalmodel/` with Pint calls using the shared UnitRegistry
**Depends on:** Phase 1 (digitalmodel acceleration), #1484 (shared UnitRegistry), #1485 (pipeline_skill.py retrofit)
**Context:** `pipeline_skill.py` successfully converted — 8 hardcoded conversion sites replaced, 39 tests passing. Shared `UnitRegistry` module in place at `src/digitalmodel/units.py`. Benchmark (#1486) shows 1.3x overhead at 1M elements — acceptable.
**Plans:** 0 plans

Plans:
- [ ] Scan and triage hardcoded conversion factors across src/digitalmodel/
- [ ] Retrofit modules with Pint Q_() calls (per-module, tests between each)
- [ ] Explore config-driven unit parsing with ureg.parse_expression()

## Progress

| Phase | Milestone | Plans | Status | Completed |
|-------|-----------|-------|--------|-----------|
| 1. Accelerate digitalmodel | v1.0 | 5/5 | Complete | 2026-03-25 |
| 2. Accelerate worldenergydata | v1.0 | 6/6 | Complete | 2026-03-26 |
| 3. GTM and marketing | v1.0 | 3/3 | Complete | 2026-03-27 |
| 4. Client acquisition | v1.0 | 3/3 | Complete | 2026-03-28 |
| 5. Nightly research automation | v1.0 | 2/2 | Complete | 2026-03-28 |
| 6. digitalmodel vision | v1.0 | 2/2 | Complete | 2026-03-29 |
| 7. Solver verification gate | v1.1 | 0/3 | Planned | — |
