# Requirements: Workspace Hub — OrcaWave Automation

**Defined:** 2026-03-30
**Core Value:** Tethering timeless engineering to a single source of truth — every calculation traces to its standard, every standard to its implementation.

## v1.1 Requirements

Requirements for OrcaWave Automation milestone. Each maps to roadmap phases.

### Problem Description & Input Generation

- [ ] **SPEC-01**: User can author a human/AI-readable problem description YAML with text blocks covering analysis intent, vessel, environment, and solver preferences
- [ ] **SPEC-02**: Deterministic modular group functions — each handles one logical group of key-value pairs (environment, hull, mesh, frequencies, solver, constraints, etc.), independently testable, codifying the manual group-by-group workflow
- [ ] **SPEC-03**: Generated OrcaWave input .yml validated via semantic comparison against existing 206+ example files — output must be as close as possible to the reference example it targets
- [ ] **SPEC-04**: Frequency normalization enforced at API boundary (Hz descending -> rad/s ascending with monotonicity assertions)
- [ ] **SPEC-05**: QTF parameter guards prevent runtime errors when qtf_calculation=false

### Calculation Report

- [ ] **REPT-01**: Standard base template covering 13 classification-society sections (document control, design basis, geometry, mesh QA, analysis config, hydrostatics, first-order results, hydrodynamic coefficients, second-order results, sensitivity studies, comparison/validation, OrcaFlex integration, conclusions), with N/A for sections not applicable to a given analysis type
- [ ] **REPT-02**: Narrative flow with engineering interpretation blocks connecting results to engineering meaning
- [ ] **REPT-03**: Automatic natural period detection via RAO peak identification, flagged against wave period range
- [ ] **REPT-04**: Tabular Excel appendix with full numerical results (RAOs, added mass, damping, mean drift) alongside HTML report
- [ ] **REPT-05**: Template extensible — new sections (e.g., sensitivity results) added as capabilities land

### Sensitivity Analysis (Starting Analysis)

- [ ] **SENS-01**: Water depth sensitivity — single-parameter sweep with comparative RAO plots
- [ ] **SENS-02**: Roll damping sensitivity — vary external damping %, compare damped vs undamped resonance
- [ ] **SENS-03**: Heading resolution sensitivity — compare results at different heading increments

### Batch Processing

- [ ] **BATCH-01**: Batch execution of all existing examples (L00-L06) through pipeline with standardized reports
- [ ] **BATCH-02**: Fleet comparison dashboard — summary HTML with pass/fail QA gates and key metrics per case
- [ ] **BATCH-03**: Per-case correctness gates (frequency monotonicity, heave RAO ~1.0 at low frequency, symmetric added mass matrix, metadata matching source model)

### OrcaFlex Integration

- [ ] **OFLEX-01**: Automated OrcaFlex vessel type .yml generated as companion deliverable alongside each report
- [ ] **OFLEX-02**: Import validation confirming OrcaWave results load into OrcaFlex without warnings, status reported in calculation report

### Infrastructure

- [x] **INFRA-01**: All spec generation, report rendering, sensitivity planning, correctness gates, and dashboard generation runs license-free on any machine
- [x] **INFRA-02**: Only solver execution and result export requires licensed machine (`licensed-win-1`); results portable via .owr + Excel

## v1.x Requirements

Deferred to future releases within the v1 cycle. Tracked but not in current roadmap.

### Report Enhancements

- **REPT-06**: Spider/tornado diagrams for sensitivity parameter ranking
- **REPT-07**: Report versioning and revision tracking (Rev A, B, C with change descriptions)
- **REPT-08**: Client branding injection (logo, company name, color scheme via branding.yaml)

### Advanced Sensitivity

- **SENS-04**: Mesh convergence study — systematic panel count refinement with convergence plots
- **SENS-05**: Draft/loading condition sensitivity — multi-draught database with different hull meshes per waterline

### Advanced Integration

- **OFLEX-03**: Multi-draught OrcaFlex vessel type database in single deliverable
- **BATCH-04**: Cross-solver comparison integration (OrcaWave + AQWA) when both licenses available

## Out of Scope

| Feature | Reason |
|---------|--------|
| Automatic mesh generation from CAD | Requires engineering judgment for BEM meshes; use pre-prepared meshes from hull panel catalog |
| Natural language problem description routing | Premature without Tier 2 NLP layer; YAML templates serve as near-NLP interface |
| PDF report generation | HTML is primary deliverable; PDF loses interactive Plotly features; add only when client explicitly requires |
| GUI for report customization | Multi-month effort for solo engineer; standardized templates with CSS theming instead |
| AI-based result interpretation | Unreliable for engineering conclusions; use deterministic QA checks with anomaly flagging |
| Real-time solver status dashboard | WebSocket complexity for solo workflow; use batch completion notifications |
| Full QTF convergence automation | Expensive, niche (slow-drift resonance only); defer to v2+ |
| Multi-body interaction reports | Additional data model complexity for coupling matrices; defer to v2+ |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SPEC-01 | Phase 8 | Pending |
| SPEC-02 | Phase 8 | Pending |
| SPEC-03 | Phase 8 | Pending |
| SPEC-04 | Phase 8 | Pending |
| SPEC-05 | Phase 8 | Pending |
| REPT-01 | Phase 9 | Pending |
| REPT-02 | Phase 9 | Pending |
| REPT-03 | Phase 9 | Pending |
| REPT-04 | Phase 9 | Pending |
| REPT-05 | Phase 9 | Pending |
| SENS-01 | Phase 10 | Pending |
| SENS-02 | Phase 10 | Pending |
| SENS-03 | Phase 10 | Pending |
| BATCH-01 | Phase 11 | Pending |
| BATCH-02 | Phase 11 | Pending |
| BATCH-03 | Phase 11 | Pending |
| OFLEX-01 | Phase 12 | Pending |
| OFLEX-02 | Phase 12 | Pending |
| INFRA-01 | Phase 7 | Complete |
| INFRA-02 | Phase 7 | Complete |

**Coverage:**
- v1.1 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0

---
*Requirements defined: 2026-03-30*
*Last updated: 2026-03-30 after roadmap creation*
