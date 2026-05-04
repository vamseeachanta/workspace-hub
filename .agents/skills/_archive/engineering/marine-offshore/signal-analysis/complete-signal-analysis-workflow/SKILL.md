---
name: signal-analysis-complete-signal-analysis-workflow
description: 'Sub-skill of signal-analysis: Complete Signal Analysis Workflow (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Complete Signal Analysis Workflow (+1)

## Complete Signal Analysis Workflow


```yaml
basename: signal_analysis_workflow

signal_analysis:
  # Step 1: Condition raw signals
  conditioning:
    flag: true
    input_file: "data/raw_stress.csv"
    output_file: "data/conditioned_stress.csv"
    operations:

*See sub-skills for full details.*

## Fatigue-Focused Analysis


```yaml
signal_analysis:
  rainflow:
    flag: true
    input_file: "data/stress_history.csv"
    output:
      cycles_file: "results/fatigue_cycles.csv"
      summary_file: "results/fatigue_summary.json"
    options:
      hysteresis_filter: 0.01  # Filter cycles < 1% of range

*See sub-skills for full details.*
