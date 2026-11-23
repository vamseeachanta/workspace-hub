---
name: solver-benchmark
version: 2.0.0
description: Run N-way diffraction solver benchmarks comparing AQWA, OrcaWave, and
  BEMRosetta results
type: reference
author: workspace-hub
category: engineering-utilities
tags:
- benchmark
- aqwa
- orcawave
- bemrosetta
- diffraction
- comparison
- validation
platforms:
- engineering
invocation: /benchmark-solvers
capabilities: []
requires: []
---

# Solver Benchmark

## When to Use This Skill

Use solver benchmarking when:
- **Validating solver setups** - Confirm all solvers produce consistent results
- **Cross-validating results** - Compare different solver outputs for the same hull
- **Identifying solver quirks** - Find solver-specific behaviors or numerical differences
- **Quality assurance** - Verify analysis methodology across tools
- **Reporting** - Generate comparison reports for documentation

## Quick Start

```bash
# Run 3-way benchmark on Unit Box (validation case)
uv run python scripts/benchmark/run_3way_benchmark.py \
    specs/modules/benchmark/unit_box_spec.yml

# Dry run (generate files, skip solver execution)
uv run python scripts/benchmark/run_3way_benchmark.py \
    specs/modules/benchmark/unit_box_spec.yml --dry-run

# Run specific solvers only
uv run python scripts/benchmark/run_3way_benchmark.py \
    spec.yml --solvers orcawave,aqwa

# Custom output directory
uv run python scripts/benchmark/run_3way_benchmark.py \
    spec.yml -o results/my_benchmark
```

## Related Skills

- **mesh-utilities** - Mesh inspection and conversion (`/mesh`)
- **hydrodynamic-analysis** - BEM theory and RAO analysis
- **orcaflex/specialist** - OrcaFlex integration

## Sub-Skills

- Troubleshooting

## Sub-Skills

- Solver Paths
- Benchmark Workflow
- Output Structure
- Consensus Levels
- Creating Benchmark Specs
- Available Hull Geometries
- Programmatic Usage
- MultiSolverComparator (+1)
- OrcaWave (via OrcFxAPI) (+3)
- Pre-Flight Validation Checklist
- Correlation Thresholds (+1)
- Mandatory Checks Before Committing Reports (+2)
- Related Work Items
