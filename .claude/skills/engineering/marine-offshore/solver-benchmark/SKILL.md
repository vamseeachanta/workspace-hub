---
name: solver-benchmark
version: 1.0.0
description: Run N-way diffraction solver benchmarks comparing AQWA, OrcaWave, and BEMRosetta results
author: workspace-hub
category: engineering-utilities
tags: [benchmark, aqwa, orcawave, bemrosetta, diffraction, comparison, validation]
platforms: [engineering]
invocation: /benchmark-solvers
---

# Solver Benchmark Skill

Run comparative benchmarks across multiple hydrodynamic diffraction solvers (AQWA, OrcaWave, BEMRosetta) with automated comparison, consensus analysis, and visualization.

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

## Available Solvers

| Solver | Executable | License | Backend |
|--------|------------|---------|---------|
| **OrcaWave** | OrcFxAPI (Python) | Orcina | BEM |
| **AQWA** | `Aqwa.exe` | ANSYS | BEM |
| **BEMRosetta** | `BEMRosetta_cl.exe` | GPL (Open Source) | NEMOH/HAMS |

### Solver Paths

Configure solver paths in the script or via environment variables:

```python
# In run_3way_benchmark.py
SOLVER_PATHS = {
    "orcawave": None,  # Uses OrcFxAPI
    "aqwa": Path("C:/Program Files/ANSYS Inc/v252/aqwa/bin/winx64/Aqwa.exe"),
    "bemrosetta": Path("D:/software/BEMRosetta/BEMRosetta_cl.exe"),
}
```

Or via environment:
```bash
export AQWA_PATH="C:/Program Files/ANSYS Inc/v252/aqwa/bin/winx64/Aqwa.exe"
export BEMROSETTA_PATH="D:/software/BEMRosetta/BEMRosetta_cl.exe"
```

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
                    Amplitude       Phase        Correlation
                    Overlay        Overlay        Heatmap
                        │               │               │
                        └───────────────┼───────────────┘
                                        │
                                        v
                              HTML + JSON Reports
```

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

## Consensus Levels

The benchmark framework classifies solver agreement:

| Level | Description | Criteria |
|-------|-------------|----------|
| **FULL** | All solvers agree | All pairs: correlation > 0.99, RMS < tolerance |
| **MAJORITY** | 2 of 3 agree | 2+ pairs meet criteria |
| **SPLIT** | Partial agreement | 1 pair meets criteria |
| **NO_CONSENSUS** | No agreement | No pairs meet criteria |

## Creating Benchmark Specs

Use the standard DiffractionSpec YAML format:

```yaml
version: "1.0"
analysis_type: diffraction

vessel:
  name: "MyHull_Benchmark"
  type: "barge"
  geometry:
    mesh_file: "path/to/mesh.gdf"
    mesh_format: gdf
    symmetry: none
    reference_point: [0.0, 0.0, 0.0]
    waterline_z: 0.0
  inertia:
    mass: 1000.0  # kg
    centre_of_gravity: [0.0, 0.0, -0.5]
    radii_of_gyration: [1.0, 1.0, 1.0]

environment:
  water_depth: 100.0
  water_density: 1025.0
  gravity: 9.80665

frequencies:
  input_type: frequency
  values: [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]

wave_headings:
  values: [0.0, 45.0, 90.0, 135.0, 180.0]
  symmetry: false

metadata:
  project: "my_benchmark"
  description: "Benchmark description"
```

## Available Hull Geometries

Pre-existing meshes for benchmarking:

| Hull | Location | Panels | Use Case |
|------|----------|--------|----------|
| **Unit Box** | `tests/.../sample_box.gdf` | 5 | Validation |
| **Barge** | `specs/.../barge.gdf` | ~900 | Practical case |
| **Spar** | `specs/.../spar.gdf` | ~1500 | Axisymmetric |
| **Cylinder** | `docs/.../Cylinder.gdf` | ~400 | WAMIT validation |

## Programmatic Usage

```python
from pathlib import Path
from scripts.benchmark.run_3way_benchmark import run_benchmark

# Run benchmark
result = run_benchmark(
    spec_path=Path("specs/modules/benchmark/unit_box_spec.yml"),
    output_dir=Path("benchmark_output/unit_box"),
    solvers=["orcawave", "aqwa", "bemrosetta"],
    dry_run=False,
)

# Check results
print(f"Success: {result.success}")
for name, sr in result.solver_results.items():
    print(f"  {name}: {sr.status}")

if result.benchmark_result and result.benchmark_result.report:
    print(f"Consensus: {result.benchmark_result.report.overall_consensus}")
```

## Framework Components

### MultiSolverComparator

```python
from digitalmodel.hydrodynamics.diffraction import (
    MultiSolverComparator,
    BenchmarkReport,
)

# Compare results from different solvers
comparator = MultiSolverComparator(
    solver_results={
        "AQWA": aqwa_results,
        "OrcaWave": orcawave_results,
        "BEMRosetta": bemrosetta_results,
    },
    tolerance=0.05,
)

# Generate report
report: BenchmarkReport = comparator.generate_report()
print(f"Overall consensus: {report.overall_consensus}")

# Export to JSON
comparator.export_report_json(Path("benchmark_report.json"))
```

### BenchmarkPlotter

```python
from digitalmodel.hydrodynamics.diffraction import BenchmarkPlotter

# Create overlay plots
plotter = BenchmarkPlotter(
    solver_results=solver_results,
    output_dir=Path("plots"),
    x_axis="period",  # or "frequency"
)

# Generate all plots
plot_paths = plotter.plot_all(headings=[0.0, 90.0, 180.0])

# Or individual plots
plotter.plot_amplitude_overlay()
plotter.plot_phase_overlay()
plotter.plot_combined_overlay()
plotter.plot_pairwise_correlation_heatmap(report)
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Solver not found | Path not configured | Set `SOLVER_PATHS` or env var |
| License error | Missing/expired license | Check license server |
| NO_CONSENSUS | Mismatched inputs | Verify spec is identical for all solvers |
| Mesh error | Incompatible format | Convert mesh using `/mesh` skill |
| Timeout | Complex geometry | Increase timeout or coarsen mesh |

## Related Skills

- **mesh-utilities** - Mesh inspection and conversion (`/mesh`)
- **hydrodynamic-analysis** - BEM theory and RAO analysis
- **orcaflex-specialist** - OrcaFlex integration

## Related Work Items

- **WRK-031** - 3-way benchmark comparison framework
- **WRK-096** - BEMRosetta installation
- **WRK-097** - Solver verification
- **WRK-098** - Unit Box spec creation
- **WRK-099** - Unit Box benchmark execution
- **WRK-100** - Barge benchmark execution

---

**Use this skill for validating solver outputs and building confidence in analysis results!**
