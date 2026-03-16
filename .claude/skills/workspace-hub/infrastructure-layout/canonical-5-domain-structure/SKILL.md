---
name: infrastructure-layout-canonical-5-domain-structure
description: 'Sub-skill of infrastructure-layout: Canonical 5-Domain Structure.'
version: 1.0.0
category: workspace
type: reference
scripts_exempt: true
---

# Canonical 5-Domain Structure

## Canonical 5-Domain Structure


```
src/<package>/infrastructure/
├── config/           ← all configuration loading and schema management
├── persistence/      ← databases, caches, provenance (formerly core/)
├── validation/       ← input validation pipelines and validators
├── utils/            ← shared utilities: data I/O, ETL, visualization, math
│   └── visualization/  ← matplotlib/plotly wrappers as a sub-package
└── solvers/ (or base_solvers/)  ← abstract solver framework, benchmarks, typed protocols
    ├── base.py           ← BaseSolver, ConfigurableSolver, AnalysisSolver
    ├── interfaces.py     ← SolverProtocol, typed protocol interfaces
    ├── structural/       ← FEM, buckling, stress elements
    ├── fatigue/          ← fatigue solvers (framework, not domain calcs)
    ├── viv/              ← VIV solver framework
    ├── marine/           ← marine solver framework
    ├── hydrodynamics/    ← hydrodynamic load calc framework
    ├── pipeline_solvers/ ← transformation / solver pipeline orchestration
    ├── well/             ← well geometry helpers
    └── benchmarks/       ← BenchmarkSuite, ReportGenerator
```

---
