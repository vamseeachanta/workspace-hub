---
name: solver-benchmark-benchmark-workflow
description: 'Sub-skill of solver-benchmark: Benchmark Workflow.'
version: 2.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# Benchmark Workflow

## Benchmark Workflow


```
DiffractionSpec (YAML)
        │
        ├──> OrcaWave Runner ──> DiffractionResults
        │
        ├──> AQWA Runner ──────> DiffractionResults
        │
        └──> BEMRosetta Runner ─> DiffractionResults
                                        │
                                        v
                            MultiSolverComparator
                                        │
                            ┌───────────┴───────────┐
                            │                       │
                    Pairwise Stats          Consensus Metrics
                    (correlation,           (FULL/MAJORITY/
                     RMS error)              SPLIT/NONE)
                            │                       │
                            └───────────┬───────────┘
                                        │
                                        v
                              BenchmarkPlotter
                                        │
                        ┌───────────────┼───────────────┐
                        │               │               │

*See sub-skills for full details.*
