---
name: orcaflex-results-comparison-basic-comparison
description: 'Sub-skill of orcaflex-results-comparison: Basic Comparison (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Basic Comparison (+1)

## Basic Comparison


```yaml
# configs/comparison_config.yml

comparison:
  # Simulations to compare
  simulations:
    - name: "Baseline"
      path: "results/baseline/.sim/mooring_analysis.sim"
    - name: "Modified_Chain"
      path: "results/modified/.sim/mooring_analysis.sim"
    - name: "Increased_Pretension"
      path: "results/high_pretension/.sim/mooring_analysis.sim"

  # Variables to compare
  variables:
    - object_pattern: "Mooring_Line_*"
      variable: "Effective Tension"
      statistic: "max"
    - object: "Vessel"
      variable: "X"
      statistic: "std"  # Standard deviation (offset)

  output:
    directory: "reports/comparison/"
    format: "html"
    include_plots: true
```


## Mooring System Comparison


```yaml
# configs/mooring_comparison.yml

comparison:
  type: "mooring_system"

  configurations:
    - name: "6-Leg Catenary"
      directory: "results/6leg_catenary/"
    - name: "8-Leg Catenary"
      directory: "results/8leg_catenary/"
    - name: "6-Leg Taut"
      directory: "results/6leg_taut/"

  analyses:
    pretension:
      enabled: true
      target_values:
        bow: 800.0     # kN
        stern: 800.0
        spring: 600.0

    stiffness:
      enabled: true
      compare_terms:
        - "K_xx"  # Surge stiffness
        - "K_yy"  # Sway stiffness
        - "K_xy"  # Coupling

    line_forces:
      enabled: true
      group_by:
        bow: ["Leg_1", "Leg_2"]
        stern: ["Leg_3", "Leg_4"]
        spring: ["Leg_5", "Leg_6"]

  output:
    report_name: "mooring_comparison"
    include_plots: true
```
