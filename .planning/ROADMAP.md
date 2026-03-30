# Workspace Hub — Roadmap

## Milestones

- ✅ **v1.0 Foundation Sprint** — Phases 1-6 (shipped 2026-03-30) — [archive](milestones/v1.0-ROADMAP.md)
- 🚧 **v1.1 OrcaWave Automation** — Phases 7-12 (in progress)

## Phases

<details>
<summary>v1.0 Foundation Sprint (Phases 1-6) -- SHIPPED 2026-03-30</summary>

- [x] Phase 1: Accelerate digitalmodel development (5/5 plans) — completed 2026-03-25
- [x] Phase 2: Accelerate worldenergydata pipelines (6/6 plans) — completed 2026-03-26
- [x] Phase 3: GTM and marketing — aceengineer-website (3/3 plans) — completed 2026-03-27
- [x] Phase 4: Client acquisition (3/3 plans) — completed 2026-03-28
- [x] Phase 5: Nightly research automation (2/2 plans) — completed 2026-03-28
- [x] Phase 6: Update plan and vision for digitalmodel repo (2/2 plans) — completed 2026-03-29

</details>

### v1.1 OrcaWave Automation (In Progress)

**Milestone Goal:** Automate the full OrcaWave vessel hull analysis workflow — from analysis type selection through to client-ready calculation reports — and prove it by generating reports for all existing examples.

- [ ] **Phase 7: Solver Verification Gate** - Confirm OrcFxAPI and Python environment functional on licensed-win-1 before any development
- [ ] **Phase 8: Spec Generation & Input Pipeline** - Deterministic problem-description-to-OrcaWave-input pipeline replacing manual YAML authoring
- [ ] **Phase 9: Single-Vessel Calculation Report** - Complete HTML calculation report meeting classification society expectations
- [ ] **Phase 10: Sensitivity Analysis** - Parameter sweep tooling for water depth, roll damping, and heading resolution
- [ ] **Phase 11: Batch Processing & Fleet Dashboard** - Run all existing examples through pipeline with fleet-wide QA dashboard
- [ ] **Phase 12: OrcaFlex Integration** - Automated vessel type export and import validation as companion deliverable

## Phase Details

### Phase 7: Solver Verification Gate
**Goal**: Confirm the license boundary architecture works — OrcFxAPI loads, solves, and exports on licensed-win-1, while all other pipeline work runs license-free on any machine
**Depends on**: Nothing (go/no-go gate for v1.1)
**Requirements**: INFRA-01, INFRA-02
**Success Criteria** (what must be TRUE):
  1. OrcFxAPI smoke test passes on licensed-win-1 (load .owd, calculate, extract one result set)
  2. `uv sync` and Python environment verified on licensed-win-1 with all project dependencies
  3. A result file (.owr + Excel) generated on licensed-win-1 can be read and processed on dev-primary (Linux) without OrcFxAPI installed
  4. Spec generation, report rendering, and data analysis code confirmed runnable on dev-primary without any licensed dependencies
**Plans**: TBD

### Phase 8: Spec Generation & Input Pipeline
**Goal**: Users can describe an analysis in a human/AI-readable YAML and get a deterministic, validated OrcaWave input file — the core innovation replacing manual YAML authoring
**Depends on**: Phase 7 (license boundary confirmed)
**Requirements**: SPEC-01, SPEC-02, SPEC-03, SPEC-04, SPEC-05
**Success Criteria** (what must be TRUE):
  1. User can author a problem description YAML with text blocks for analysis intent, vessel, environment, and solver preferences — and the system produces a complete OrcaWave input .yml
  2. Each group function (environment, hull, mesh, frequencies, solver, constraints, etc.) is independently testable and produces deterministic output for the same input
  3. Generated .yml files pass semantic comparison against existing 206+ example files — output matches the closest reference example within defined tolerance
  4. Frequency values entering the pipeline in any unit convention are normalized to rad/s ascending with monotonicity assertions at the API boundary
  5. Setting qtf_calculation=false never triggers runtime errors from QTF-dependent parameters
**Plans**: TBD

### Phase 9: Single-Vessel Calculation Report
**Goal**: Users receive a client-ready HTML calculation report for any single vessel that meets classification society expectations — narrative structure, integrated plots, QA summaries, and full numerical appendix
**Depends on**: Phase 8 (spec pipeline provides validated input data)
**Requirements**: REPT-01, REPT-02, REPT-03, REPT-04, REPT-05
**Success Criteria** (what must be TRUE):
  1. Running the report generator on a completed OrcaWave analysis produces an HTML report covering all 13 classification-society sections, with N/A rendered cleanly for non-applicable sections
  2. Report contains narrative interpretation blocks that connect numerical results to engineering meaning (not just data tables)
  3. Natural periods are automatically detected via RAO peak identification and flagged against the wave period range in the report
  4. A companion Excel workbook with full numerical results (RAOs, added mass, damping, mean drift) is generated alongside each HTML report
  5. Adding a new report section (e.g., sensitivity results) requires only registering a new section module — no changes to the base template or data model
**Plans**: TBD
**UI hint**: yes

### Phase 10: Sensitivity Analysis
**Goal**: Users can run single-parameter sweeps to understand how water depth, roll damping, and heading resolution affect vessel response — eliminating guesswork before committing to full analysis
**Depends on**: Phase 8 (spec generation creates variant specs), Phase 9 (report sections render sensitivity results)
**Requirements**: SENS-01, SENS-02, SENS-03
**Success Criteria** (what must be TRUE):
  1. User can specify a range of water depths and get comparative RAO plots showing response variation across the sweep
  2. User can vary external roll damping percentage and see damped vs undamped resonance comparison in the output
  3. User can compare results at different heading increments (e.g., 15-degree vs 5-degree resolution) to verify heading convergence
**Plans**: TBD

### Phase 11: Batch Processing & Fleet Dashboard
**Goal**: All existing examples (L00-L06) run through the pipeline producing standardized reports, with a fleet-wide dashboard showing pass/fail QA status per case
**Depends on**: Phase 9 (single-vessel report works), Phase 10 (sensitivity analysis provides per-case quality patterns)
**Requirements**: BATCH-01, BATCH-02, BATCH-03
**Success Criteria** (what must be TRUE):
  1. Running the batch processor against all existing examples (L00-L06) produces a standardized report for each case without manual intervention
  2. A fleet comparison dashboard (HTML) shows pass/fail QA gates and key metrics per case in a single summary view
  3. Per-case correctness gates automatically verify frequency monotonicity, heave RAO approaching 1.0 at low frequency, symmetric added mass matrix, and metadata matching the source model
**Plans**: TBD
**UI hint**: yes

### Phase 12: OrcaFlex Integration
**Goal**: Every completed diffraction analysis automatically produces a validated OrcaFlex vessel type file as a companion deliverable
**Depends on**: Phase 11 (batch pipeline proven, correctness gates in place)
**Requirements**: OFLEX-01, OFLEX-02
**Success Criteria** (what must be TRUE):
  1. Running the pipeline produces an OrcaFlex vessel type .yml alongside each calculation report — no separate manual export step
  2. The generated vessel type file loads into OrcaFlex without warnings, and the import validation status is reported in the calculation report
**Plans**: TBD

## Standalone Phases

### Phase 1000: Cross-AI Parallel Planning and Cross-Review (COMPLETE)

**Goal:** Add cross-AI parallel planning and parallel cross-review to the GSD issue workflow
**Context:** GitHub #1501. Extends existing infrastructure with optional modes for multi-provider planning and review.
**Requirements:** [XCONFIG-01, XCONFIG-02, XCONFIG-03, XREV-01, XREV-02, XPLAN-01, XPLAN-02, XPLAN-03, XSKILL-01, XSKILL-02]
**Plans:** 3/3 complete

Plans:
- [x] 1000-01: Config contracts (routing-config, behavior-contract, delegation templates)
- [x] 1000-02: cross-plan.sh script
- [x] 1000-03: GSD skill integration

## Backlog

<details>
<summary>Backlog phases (999.x) -- promote with $gsd-review-backlog</summary>

### Phase 999.1: Ship Plan CAD Pipeline — Curve reconstruction for 3D hull lofting (BACKLOG)

**Goal:** Reconstruct continuous hull curves from fragmented skeleton vectorization, enabling 3D hull surface generation via FreeCAD/Gmsh
**Context:** WRK-5055 Phase 1 complete — 110 SNAME ship plans cataloged, 986 pages scanned, skeleton DXFs generated for all profiles and 3 lines plans (BB-45 USS Colorado, EC2-S-C1 Liberty Ship, SS-563 USS Tang). FreeCAD `Part.makeLoft()` proven functional but current vectorization produces fragmented pixel-edge traces unsuitable for direct lofting.
**Plans:** 0 plans

### Phase 999.2: Wind Energy, Turbines & Fitness-for-Service Vision (BACKLOG)

**Goal:** Add calculation modules for wind/turbine structures and fitness-for-service assessments
**Plans:** 0 plans

### Phase 999.3: CAD/CAM & Manufacturing Vision (BACKLOG)

**Goal:** Define and implement CAD/CAM and manufacturing capabilities
**Plans:** 0 plans

### Phase 999.4: Extend Autoresearch to Agent & Template Definitions (BACKLOG)

**Goal:** Generalize the skill-autoresearch loop to iterate on agent definitions, research templates, and workflow configs
**Plans:** 0 plans

### Phase 999.5: High-Iteration Autoresearch with Compounding Improvements (BACKLOG)

**Goal:** Increase autoresearch iteration depth from single-pass to multi-cycle per target per night
**Plans:** 0 plans

</details>

## Progress

**Execution Order:** Phase 7 -> 8 -> 9 -> 10 -> 11 -> 12

| Phase | Milestone | Plans | Status | Completed |
|-------|-----------|-------|--------|-----------|
| 1. Accelerate digitalmodel | v1.0 | 5/5 | Complete | 2026-03-25 |
| 2. Accelerate worldenergydata | v1.0 | 6/6 | Complete | 2026-03-26 |
| 3. GTM and marketing | v1.0 | 3/3 | Complete | 2026-03-27 |
| 4. Client acquisition | v1.0 | 3/3 | Complete | 2026-03-28 |
| 5. Nightly research automation | v1.0 | 2/2 | Complete | 2026-03-28 |
| 6. digitalmodel vision | v1.0 | 2/2 | Complete | 2026-03-29 |
| 7. Solver Verification Gate | v1.1 | 0/? | Not started | - |
| 8. Spec Generation & Input Pipeline | v1.1 | 0/? | Not started | - |
| 9. Single-Vessel Calculation Report | v1.1 | 0/? | Not started | - |
| 10. Sensitivity Analysis | v1.1 | 0/? | Not started | - |
| 11. Batch Processing & Fleet Dashboard | v1.1 | 0/? | Not started | - |
| 12. OrcaFlex Integration | v1.1 | 0/? | Not started | - |
| 1000. Cross-AI parallel planning | — | 3/3 | Complete | 2026-03-30 |
