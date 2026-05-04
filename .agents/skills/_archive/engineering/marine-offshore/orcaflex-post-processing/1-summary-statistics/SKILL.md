---
name: orcaflex-post-processing-1-summary-statistics
description: 'Sub-skill of orcaflex-post-processing: 1. Summary Statistics (+4).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Summary Statistics (+4)

## 1. Summary Statistics


Extract min, max, mean, std dev for all monitored variables.

```yaml
orcaflex:
  postprocess:
    summary:
      flag: true
      variables:
        - object: "Line1"
          variable_name: "Effective Tension"
        - object: "Vessel1"
          variable_name: "X"
      output_format: csv  # csv, json, or xlsx
      output_path: "results/summary/"
```

## 2. Linked Statistics


Compute correlations and linked values between variables.

```yaml
orcaflex:
  postprocess:
    linked_statistics:
      flag: true
      primary_variable:
        object: "Line1"
        variable_name: "Effective Tension"

*See sub-skills for full details.*

## 3. Range Graphs


Generate envelope plots showing variable ranges.

```yaml
orcaflex:
  postprocess:
    RangeGraph:
      flag: true
      objects:
        - name: "Line1"
          variables:

*See sub-skills for full details.*

## 4. Time Series


Extract and plot time-domain data.

```yaml
orcaflex:
  postprocess:
    time_series:
      flag: true
      variables:
        - object: "Vessel1"
          variable_name: "X"

*See sub-skills for full details.*

## 5. Histograms


Generate probability distributions.

```yaml
orcaflex:
  postprocess:
    visualization:
      flag: true
      histogram:
        enabled: true
        variables:

*See sub-skills for full details.*
