---
name: solver-benchmark-output-structure
description: 'Sub-skill of solver-benchmark: Output Structure.'
version: 2.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# Output Structure

## Output Structure


```
benchmark_output/<spec_name>_<timestamp>/
├── benchmark_summary.json      # Orchestration summary
├── orcawave/                   # OrcaWave outputs
│   ├── input/                  # Generated input files
│   ├── results/                # Solver results
│   └── orcawave.log
├── aqwa/                       # AQWA outputs
│   ├── input/
│   ├── results/
│   └── aqwa.log
├── bemrosetta/                 # BEMRosetta outputs
│   ├── nemoh_case/
│   └── bemrosetta.log
└── benchmark_comparison/       # Comparison results
    ├── benchmark_report.json
    ├── benchmark_report.html
    ├── benchmark_amplitude.html
    ├── benchmark_phase.html
    ├── benchmark_combined.html
    └── benchmark_heatmap.html
```
