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
from digitalmodel.solvers.orcaflex.operability_analysis import OperabilityAnalyzer

# Initialize analyzer
analyzer = OperabilityAnalyzer(
    simulation_directory="results/.sim/",
    output_directory="reports/operability/"
)

# Generate operability envelope

*See sub-skills for full details.*
### Weather Downtime Calculation

```python
from digitalmodel.solvers.orcaflex.operability_analysis import OperabilityAnalyzer
import pandas as pd

analyzer = OperabilityAnalyzer(
    simulation_directory="results/.sim/",
    output_directory="reports/"
)

# Load wave scatter diagram

*See sub-skills for full details.*
### Critical Headings Analysis

```python
from digitalmodel.solvers.orcaflex.operability_analysis import OperabilityAnalyzer

analyzer = OperabilityAnalyzer(
    simulation_directory="results/.sim/",
    output_directory="reports/"
)

# Identify critical headings
critical = analyzer.generate_critical_headings_report(

*See sub-skills for full details.*
### Comprehensive Report Generation

```python
from digitalmodel.solvers.orcaflex.operability_analysis import OperabilityAnalyzer

analyzer = OperabilityAnalyzer(
    simulation_directory="results/.sim/",
    output_directory="reports/"
)

# Generate comprehensive HTML report with all analyses
report_path = analyzer.generate_comprehensive_report(

*See sub-skills for full details.*

## Related Skills

- orcaflex-modeling - Run OrcaFlex simulations
- orcaflex-post-processing - Extract results
- orcaflex-extreme-analysis - Extreme value extraction
- mooring-design - Mooring system design

## References

- API RP 2SK: Design and Analysis of Stationkeeping Systems
- DNV-OS-E301: Position Mooring
- ISO 19901-7: Stationkeeping Systems
- Source: `src/digitalmodel/solvers/orcaflex/operability_analysis.py`

## Sub-Skills

- Basic Operability Configuration (+1)
- Simulation Setup (+2)

## Sub-Skills

- Error Handling

## Sub-Skills

- Version Metadata
- [[1.0.0] - 2026-01-17](100-2026-01-17/SKILL.md)
- Operability Workflow
- Operability Envelope Plot (+2)
- CSV Matrix Format
- With OrcaFlex Modeling (+1)
