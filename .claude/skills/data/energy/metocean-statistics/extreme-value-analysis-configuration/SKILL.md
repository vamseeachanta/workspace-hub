---
name: metocean-statistics-extreme-value-analysis-configuration
description: 'Sub-skill of metocean-statistics: Extreme Value Analysis Configuration
  (+3).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Extreme Value Analysis Configuration (+3)

## Extreme Value Analysis Configuration


```yaml
analysis:
  name: extreme_value_analysis
  type: extreme_value

  # Method selection
  method: block_maxima  # Options: block_maxima, peak_over_threshold
  block_size: year      # For block_maxima: year, month, season

  # Distribution fitting

*See sub-skills for full details.*

## Joint Probability Configuration


```yaml
joint_analysis:
  name: hs_tp_joint_distribution

  # Variables
  variables:
    x: wave_height_m
    y: wave_period_s

  # Distribution fitting

*See sub-skills for full details.*

## Directional Analysis Configuration


```yaml
directional_analysis:
  name: wave_directional_stats

  # Sector definition
  sectors: 16           # Options: 8, 12, 16
  convention: from      # Options: from, to (direction waves come from)

  # Parameters to analyze
  parameters:

*See sub-skills for full details.*

## Monthly Statistics Configuration


```yaml
temporal_analysis:
  name: monthly_statistics

  # Aggregation period
  period: monthly       # Options: monthly, seasonal, annual

  # Statistics to calculate
  statistics:
    - mean

*See sub-skills for full details.*
