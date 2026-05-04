---
name: solver-benchmark-multisolvercomparator
description: 'Sub-skill of solver-benchmark: MultiSolverComparator (+1).'
version: 2.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# MultiSolverComparator (+1)

## MultiSolverComparator


```python
from digitalmodel.hydrodynamics.diffraction import (
    MultiSolverComparator,
    BenchmarkReport,
)

# Compare results from different solvers
comparator = MultiSolverComparator(
    solver_results={
        "AQWA": aqwa_results,

*See sub-skills for full details.*

## BenchmarkPlotter


```python
from digitalmodel.hydrodynamics.diffraction import BenchmarkPlotter

# Create overlay plots
plotter = BenchmarkPlotter(
    solver_results=solver_results,
    output_dir=Path("plots"),
    x_axis="period",  # or "frequency"
)


*See sub-skills for full details.*
