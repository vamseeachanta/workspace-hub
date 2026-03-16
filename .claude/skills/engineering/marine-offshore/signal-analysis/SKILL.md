---
name: signal-analysis
description: Perform signal processing, rainflow cycle counting, and spectral analysis
  for fatigue and time series data. Use for analyzing stress time histories, computing
  FFT/PSD, extracting fatigue cycles (ASTM E1049-85), and batch processing OrcaFlex
  signals.
updated: '2026-01-07'
capabilities: []
requires: []
see_also:
- signal-analysis-version-metadata
- signal-analysis-100-2026-01-07
- signal-analysis-1-rainflow-cycle-counting-astm-e1049-85
- signal-analysis-complete-signal-analysis-workflow
- signal-analysis-rainflow-cycles-csv
tags: []
scripts_exempt: true
category: engineering
version: 1.0.0
---

# Signal Analysis

## When to Use

- Analyzing fatigue from stress/load time series
- Computing rainflow cycles for damage calculation
- FFT and power spectral density analysis
- Frequency spectrum characterization
- Batch processing OrcaFlex simulation signals
- Time series conditioning and filtering
- Converting time-domain data to frequency-domain

## Prerequisites

- Python environment with `digitalmodel` package installed
- Time series data in CSV, Excel, or OrcaFlex format
- For OrcaFlex signals: completed .sim files

## Python API

### Rainflow Cycle Counting

```python
from digitalmodel.signal_processing.signal_analysis.rainflow import RainflowCounter

# Initialize counter
counter = RainflowCounter()

# Load time history
import pandas as pd
data = pd.read_csv("stress_time_history.csv")
time = data["time"].values

*See sub-skills for full details.*
### Spectral Analysis

```python
from digitalmodel.signal_processing.signal_analysis.spectral import SpectralAnalyzer
import numpy as np

# Initialize analyzer
analyzer = SpectralAnalyzer()

# Load signal
data = pd.read_csv("motion_time_history.csv")
time = data["time"].values

*See sub-skills for full details.*
### Time Series Processing

```python
from digitalmodel.signal_processing.signal_analysis.time_series import TimeSeriesProcessor

# Initialize processor
processor = TimeSeriesProcessor()

# Load raw data
data = pd.read_csv("raw_signal.csv")
time = data["time"].values
signal = data["stress"].values

*See sub-skills for full details.*
### OrcaFlex Signal Extraction

```python
from digitalmodel.signal_processing.signal_analysis.orcaflex_signals import OrcaFlexSignalExtractor
from pathlib import Path

# Initialize extractor
extractor = OrcaFlexSignalExtractor()

# Extract time history from single .sim file
sim_file = Path("simulation.sim")
time, tension = extractor.extract_time_history(

*See sub-skills for full details.*
### Generic Time Series Reader

```python
from digitalmodel.signal_processing.signal_analysis.readers import GenericTimeSeriesReader

# Auto-detect file format and load
reader = GenericTimeSeriesReader()

# Read CSV
data = reader.read("data/measurements.csv")

# Read Excel

*See sub-skills for full details.*

## Related Skills

- [fatigue-analysis](../fatigue-analysis/SKILL.md) - Use rainflow cycles for fatigue damage calculation
- [orcaflex-post-processing](../orcaflex-post-processing/SKILL.md) - Extract time histories from OrcaFlex
- [structural-analysis](../structural-analysis/SKILL.md) - Stress analysis for signal generation

## References

- ASTM E1049-85: Standard Practices for Cycle Counting in Fatigue Analysis
- Welch, P.D. (1967): The Use of FFT for Estimation of Power Spectra
- DNV-RP-C203: Fatigue Design of Offshore Steel Structures

## Sub-Skills

- [Signal Quality (+2)](signal-quality/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-07](100-2026-01-07/SKILL.md)
- [1. Rainflow Cycle Counting (ASTM E1049-85) (+4)](1-rainflow-cycle-counting-astm-e1049-85/SKILL.md)
- [Complete Signal Analysis Workflow (+1)](complete-signal-analysis-workflow/SKILL.md)
- [Rainflow Cycles CSV (+2)](rainflow-cycles-csv/SKILL.md)
