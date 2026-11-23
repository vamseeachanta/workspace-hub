---
name: orcaflex-results-comparison
description: Compare results across multiple OrcaFlex simulations for design verification,
  sensitivity studies, and configuration comparison. Includes pretension, stiffness,
  and force distribution analysis.
type: reference
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- compare simulations
- results comparison
- sensitivity study
- design comparison
- configuration comparison
- pretension comparison
- stiffness comparison
- mooring comparison
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcaflex Results Comparison

## When to Use

- Comparing design alternatives
- Sensitivity analysis (depth, heading, sea state)
- Baseline vs modified configuration
- Design verification against target values
- Multi-configuration optimization
- Mooring system comparison
- Installation sequence comparison

## Prerequisites

- Multiple OrcaFlex simulation results (.sim files or extracted CSV)
- Python environment with `digitalmodel` package installed
- Consistent variable naming across simulations

## Python API

### Basic Comparison

```python
from digitalmodel.solvers.orcaflex.analysis.comparative import MooringComparativeAnalysis
from pathlib import Path

# Initialize analyzer
analyzer = MooringComparativeAnalysis(
    results_directory=Path("results/")
)

# Compare pretensions

*See sub-skills for full details.*
### Stiffness Comparison

```python
from digitalmodel.solvers.orcaflex.analysis.comparative import MooringComparativeAnalysis

analyzer = MooringComparativeAnalysis(results_directory=Path("results/"))

# Compare stiffness matrices
stiffness_comparison = analyzer.compare_stiffness(
    configurations=["6_leg", "8_leg", "taut_leg"]
)


*See sub-skills for full details.*
### Line Force Distribution

```python
from digitalmodel.solvers.orcaflex.analysis.comparative import MooringComparativeAnalysis

analyzer = MooringComparativeAnalysis(results_directory=Path("results/"))

# Compare force distribution by line groups
force_comparison = analyzer.compare_line_stiffness_distribution(
    configurations=["baseline", "optimized"],
    line_groups={
        "bow": ["Leg_1", "Leg_2"],

*See sub-skills for full details.*
### Multi-Simulation Response Comparison

```python
import OrcFxAPI
from pathlib import Path
import pandas as pd
import numpy as np

def compare_simulation_responses(
    sim_files: list,
    config: dict
) -> pd.DataFrame:

*See sub-skills for full details.*
### Sensitivity Analysis

```python
def sensitivity_analysis(
    parameter_name: str,
    parameter_values: list,
    result_variable: str,
    results: pd.DataFrame
) -> dict:
    """
    Analyze sensitivity of result to parameter.
    """

*See sub-skills for full details.*

## Related Skills

- orcaflex-post-processing - Extract results
- orcaflex-extreme-analysis - Extreme values
- orcaflex-operability - Multi-sea-state analysis
- mooring-design - Mooring system design

## References

- API RP 2SK: Design and Analysis of Stationkeeping Systems
- DNV-OS-E301: Position Mooring
- Source: `src/digitalmodel/solvers/orcaflex/analysis/comparative.py`

## Sub-Skills

- Basic Comparison (+1)
- Simulation Setup (+2)

## Sub-Skills

- Error Handling

## Sub-Skills

- Version Metadata
- [1.0.0] - 2026-01-17
- 1. Pretension Comparison (+3)
- Comparison Bar Chart (+1)
- Comparison Summary Table (+1)
