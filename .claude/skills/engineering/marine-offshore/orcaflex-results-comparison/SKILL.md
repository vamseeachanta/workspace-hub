---
name: orcaflex-results-comparison
description: Compare results across multiple OrcaFlex simulations for design verification,
  sensitivity studies, and configuration comparison. Includes pretension, stiffness,
  and force distribution analysis.
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
see_also:
- orcaflex-results-comparison-version-metadata
- orcaflex-results-comparison-100-2026-01-17
- orcaflex-results-comparison-1-pretension-comparison
- orcaflex-results-comparison-comparison-bar-chart
- orcaflex-results-comparison-comparison-summary-table
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
from digitalmodel.orcaflex.analysis.comparative import MooringComparativeAnalysis
from pathlib import Path

# Initialize analyzer
analyzer = MooringComparativeAnalysis(
    results_directory=Path("results/")
)

# Compare pretensions

*See sub-skills for full details.*
### Stiffness Comparison

```python
from digitalmodel.orcaflex.analysis.comparative import MooringComparativeAnalysis

analyzer = MooringComparativeAnalysis(results_directory=Path("results/"))

# Compare stiffness matrices
stiffness_comparison = analyzer.compare_stiffness(
    configurations=["6_leg", "8_leg", "taut_leg"]
)


*See sub-skills for full details.*
### Line Force Distribution

```python
from digitalmodel.orcaflex.analysis.comparative import MooringComparativeAnalysis

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

- [orcaflex-post-processing](../orcaflex-post-processing/SKILL.md) - Extract results
- [orcaflex-extreme-analysis](../orcaflex-extreme-analysis/SKILL.md) - Extreme values
- [orcaflex-operability](../orcaflex-operability/SKILL.md) - Multi-sea-state analysis
- [mooring-design](../mooring-design/SKILL.md) - Mooring system design

## References

- API RP 2SK: Design and Analysis of Stationkeeping Systems
- DNV-OS-E301: Position Mooring
- Source: `src/digitalmodel/modules/orcaflex/analysis/comparative.py`

## Sub-Skills

- [Basic Comparison (+1)](basic-comparison/SKILL.md)
- [Simulation Setup (+2)](simulation-setup/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-17](100-2026-01-17/SKILL.md)
- [1. Pretension Comparison (+3)](1-pretension-comparison/SKILL.md)
- [Comparison Bar Chart (+1)](comparison-bar-chart/SKILL.md)
- [Comparison Summary Table (+1)](comparison-summary-table/SKILL.md)
