---
name: orcaflex-operability
description: Perform operability analysis combining multiple sea states to assess
  system availability and weather downtime. Generate operability envelopes, critical
  heading analysis, and downtime calculations from wave scatter diagrams.
type: reference
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- operability analysis
- weather downtime
- operability envelope
- sea state analysis
- weather window
- operational limits
- critical headings
- wave scatter
- annual downtime
capabilities: []
requires: []
tags: []
scripts_exempt: true
---

# Orcaflex Operability

## When to Use

- Operability envelope generation for mooring systems
- Weather downtime calculations from scatter diagrams
- Critical heading identification for design loads
- Multi-sea-state analysis (1yr, 10yr, 100yr return periods)
- Tension limit assessment (intact vs damaged conditions)
- Annual operational availability studies
- Polar coordinate visualization of system limits

## Prerequisites

- OrcaFlex simulation results (.sim files) for multiple headings
- Wave scatter diagram (Hs-Tp probability matrix)
- Python environment with `digitalmodel` package installed
- Tension limits for intact and damaged conditions

## Python API

### Basic Operability Analysis

```python
from digitalmodel.orcaflex.operability_analysis import OperabilityAnalyzer

# Initialize analyzer
analyzer = OperabilityAnalyzer(
    simulation_directory="results/.sim/",
    output_directory="reports/operability/"
)

# Generate operability envelope

*See sub-skills for full details.*
### Weather Downtime Calculation

```python
from digitalmodel.orcaflex.operability_analysis import OperabilityAnalyzer
import pandas as pd

analyzer = OperabilityAnalyzer(
    simulation_directory="results/.sim/",
    output_directory="reports/"
)

# Load wave scatter diagram

*See sub-skills for full details.*
### Critical Headings Analysis

```python
from digitalmodel.orcaflex.operability_analysis import OperabilityAnalyzer

analyzer = OperabilityAnalyzer(
    simulation_directory="results/.sim/",
    output_directory="reports/"
)

# Identify critical headings
critical = analyzer.generate_critical_headings_report(

*See sub-skills for full details.*
### Comprehensive Report Generation

```python
from digitalmodel.orcaflex.operability_analysis import OperabilityAnalyzer

analyzer = OperabilityAnalyzer(
    simulation_directory="results/.sim/",
    output_directory="reports/"
)

# Generate comprehensive HTML report with all analyses
report_path = analyzer.generate_comprehensive_report(

*See sub-skills for full details.*

## Related Skills

- [orcaflex-modeling](../orcaflex-modeling/SKILL.md) - Run OrcaFlex simulations
- [orcaflex-post-processing](../orcaflex-post-processing/SKILL.md) - Extract results
- [orcaflex-extreme-analysis](../orcaflex-extreme-analysis/SKILL.md) - Extreme value extraction
- [mooring-design](../mooring-design/SKILL.md) - Mooring system design

## References

- API RP 2SK: Design and Analysis of Stationkeeping Systems
- DNV-OS-E301: Position Mooring
- ISO 19901-7: Stationkeeping Systems
- Source: `src/digitalmodel/modules/orcaflex/operability_analysis.py`

## Sub-Skills

- [Basic Operability Configuration (+1)](basic-operability-configuration/SKILL.md)
- [Simulation Setup (+2)](simulation-setup/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-17](100-2026-01-17/SKILL.md)
- [Operability Workflow](operability-workflow/SKILL.md)
- [Operability Envelope Plot (+2)](operability-envelope-plot/SKILL.md)
- [CSV Matrix Format](csv-matrix-format/SKILL.md)
- [With OrcaFlex Modeling (+1)](with-orcaflex-modeling/SKILL.md)
