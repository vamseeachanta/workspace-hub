---
name: orcaflex
description: OrcaFlex marine dynamic analysis — modeling, analysis, post-processing, and validation
type: domain
---

# OrcaFlex Skills

Root skill for OrcaFlex marine dynamic analysis workflows.

## References

- `references/current-rudder-resultant-reporting.md` — checklist for OCIMF-style current vs rudder vs total/resultant force and yaw-moment report sections, including static Markdown/PDF requirements.

## Sub-Skills

### Modeling
- **modeling/** — Core OrcaFlex model building
- **model-generator/** — Automated model generation from templates
- **model-sanitization/** — Model cleanup and validation
- **monolithic-to-modular/** — Split large models into modular components

### Environment & Setup
- **environment-config/** — Environmental load configuration
- **vessel-setup/** — Vessel and floating body setup
- **rao-import/** — RAO data import and validation

### Analysis
- **extreme-analysis/** — Extreme response analysis
- **modal-analysis/** — Modal and eigenvalue analysis
- **installation-analysis/** — Marine installation simulations
- **jumper-analysis/** — Jumper and flexible riser analysis
- **mooring-iteration/** — Mooring system design iteration
- **operability/** — Weather window and operability assessment

### Post-Processing
- **post-processing/** — Results extraction and processing
- **results-comparison/** — Compare results across load cases
- **visualization/** — Plots and animation generation

### Validation
- **code-check/** — OrcaFlex model code compliance checks
- **spec-audit/** — Specification compliance audit
- **static-debug/** — Static analysis debugging
- **yaml-gotchas/** — Common YAML configuration pitfalls

### Review References
- **references/current-vs-rudder-force-review.md** — Pattern for comparing OCIMF-style hull current forces against rudder-induced forces; includes component/resultant table structure, coefficient-provenance caveat, and interpretation checklist.

### Utilities
- **batch-manager/** — Batch run management
- **file-conversion/** — File format conversion
- **line-wizard/** — Line type configuration wizard
- **specialist/** — General OrcaFlex expert guidance
