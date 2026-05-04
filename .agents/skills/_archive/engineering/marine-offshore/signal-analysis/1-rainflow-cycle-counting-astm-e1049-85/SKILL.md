---
name: signal-analysis-1-rainflow-cycle-counting-astm-e1049-85
description: 'Sub-skill of signal-analysis: 1. Rainflow Cycle Counting (ASTM E1049-85)
  (+4).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Rainflow Cycle Counting (ASTM E1049-85) (+4)

## 1. Rainflow Cycle Counting (ASTM E1049-85)


Extract stress/load cycles for fatigue analysis using industry-standard rainflow algorithm.

```yaml
signal_analysis:
  rainflow:
    flag: true
    input_file: "data/stress_time_history.csv"
    time_column: "time"
    signal_column: "stress"
    output:

*See sub-skills for full details.*

## 2. FFT Spectral Analysis


Compute frequency content using Fast Fourier Transform.

```yaml
signal_analysis:
  fft:
    flag: true
    input_file: "data/motion_time_history.csv"
    time_column: "time"
    signal_column: "heave"
    output:

*See sub-skills for full details.*

## 3. Power Spectral Density (Welch Method)


Estimate power spectral density with reduced variance using overlapping segments.

```yaml
signal_analysis:
  psd:
    flag: true
    input_file: "data/vessel_motion.csv"
    time_column: "time"
    signal_columns:
      - "surge"

*See sub-skills for full details.*

## 4. Time Series Conditioning


Prepare raw time series for analysis with filtering and preprocessing.

```yaml
signal_analysis:
  conditioning:
    flag: true
    input_file: "data/raw_signal.csv"
    output_file: "data/conditioned_signal.csv"
    operations:
      - type: "resample"

*See sub-skills for full details.*

## 5. OrcaFlex Signal Batch Processing


Process multiple OrcaFlex time histories in parallel.

```yaml
signal_analysis:
  orcaflex_batch:
    flag: true
    sim_directory: "results/.sim/"
    sim_pattern: "*.sim"
    variables:
      - object: "Line1"

*See sub-skills for full details.*
