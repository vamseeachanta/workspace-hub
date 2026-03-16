---
name: orcaflex-extreme-analysis
description: Extract extreme response values with linked statistics from OrcaFlex
  simulations. Use for design load identification, max/min extraction with associated
  values, and extreme event characterization.
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- extreme analysis
- max tension
- linked statistics
- extreme values
- design loads
- maximum response
- associated values
- peak extraction
capabilities: []
requires: []
see_also:
- orcaflex-extreme-analysis-version-metadata
- orcaflex-extreme-analysis-100-2026-01-17
- orcaflex-extreme-analysis-linked-statistics
- orcaflex-extreme-analysis-linked-statistics-csv
- orcaflex-extreme-analysis-1-design-load-identification
tags: []
scripts_exempt: true
---

# Orcaflex Extreme Analysis

## When to Use

- Extracting maximum/minimum values from simulations
- Identifying design loads for structural analysis
- Finding associated values at extreme events
- Characterizing vessel motions at peak tensions
- Riser curvature at maximum tension conditions
- Wave conditions at extreme responses
- Multi-variable correlation at extremes

## Prerequisites

- OrcaFlex simulation results (.sim files)
- Python environment with `digitalmodel` package installed
- Knowledge of variables to extract (object names, variable names)

## Python API

### Basic Linked Statistics

```python
from digitalmodel.orcaflex.opp_linkedstatistics import OPPLinkedStatistics

# Initialize extractor
extractor = OPPLinkedStatistics()

# Configure extraction
config = {
    "primary": {
        "object": "Mooring_Line_1",

*See sub-skills for full details.*
### Direct OrcFxAPI Usage

```python
import OrcFxAPI
from pathlib import Path

def extract_extremes_with_linked(sim_file: str, config: dict) -> dict:
    """
    Extract extreme values with linked statistics.

    Args:
        sim_file: Path to .sim file

*See sub-skills for full details.*
### Batch Extreme Analysis

```python
from digitalmodel.orcaflex.opp_linkedstatistics import OPPLinkedStatistics
from pathlib import Path
import pandas as pd

def batch_extreme_analysis(sim_directory: str, config: dict) -> pd.DataFrame:
    """
    Extract extremes from multiple simulations.
    """
    extractor = OPPLinkedStatistics()

*See sub-skills for full details.*
### Range Graph Extremes

```python
from digitalmodel.orcaflex.opp_range_graph import OPPRangeGraph

# Extract range graph (min/max/mean along arc length)
range_extractor = OPPRangeGraph()

config = {
    "object": "Riser",
    "variables": ["Effective Tension", "Curvature", "Bend Moment"],
    "arc_length_range": [0, 1500]  # meters

*See sub-skills for full details.*

## Related Skills

- [orcaflex-post-processing](../orcaflex-post-processing/SKILL.md) - General post-processing
- [orcaflex-operability](../orcaflex-operability/SKILL.md) - Multi-sea-state analysis
- [orcaflex-results-comparison](../orcaflex-results-comparison/SKILL.md) - Compare multiple results
- [fatigue-analysis](../fatigue-analysis/SKILL.md) - Fatigue from time histories

## References

- OrcaFlex Results: Linked Statistics
- OrcFxAPI Documentation
- Source: `src/digitalmodel/modules/orcaflex/opp_linkedstatistics.py`
- Source: `src/digitalmodel/modules/orcaflex/opp_range_graph.py`

## Sub-Skills

- [Basic Extreme Extraction (+1)](basic-extreme-extraction/SKILL.md)
- [Variable Selection (+2)](variable-selection/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-17](100-2026-01-17/SKILL.md)
- [Linked Statistics (+1)](linked-statistics/SKILL.md)
- [Linked Statistics CSV (+1)](linked-statistics-csv/SKILL.md)
- [1. Design Load Identification (+2)](1-design-load-identification/SKILL.md)
