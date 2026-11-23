---
name: orcaflex-mooring-iteration-basic-configuration
description: 'Sub-skill of orcaflex-mooring-iteration: Basic Configuration (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Basic Configuration (+1)

## Basic Configuration


```yaml
# configs/mooring_iteration.yml

iteration:
  method: "scipy"  # scipy, newton_raphson, or ea_based

  convergence:
    tolerance: 1.0          # % error tolerance
    min_tolerance: 0.5      # Minimum acceptable
    max_iterations: 50
    damping_factor: 0.7     # Under-relaxation

  jacobian:
    perturbation_factor: 0.001
    min_perturbation: 0.1   # meters
    cache_enabled: true

  vessel_config:
    fix_vessels: true
    vessels_to_fix: ["FPSO"]
    fix_degrees_of_freedom: ["X", "Y", "Z", "Rotation 1", "Rotation 2", "Rotation 3"]

lines:
  - name: "Mooring_Line_1"
    target_tension: 800.0     # kN
    tolerance: 1.0            # % specific tolerance
    variable_section: 1       # Section index to adjust

  - name: "Mooring_Line_2"
    target_tension: 800.0
    tolerance: 1.0
    variable_section: 1

  - name: "Mooring_Line_3"
    target_tension: 800.0
    tolerance: 1.0
    variable_section: 1
```


## Advanced Configuration


```yaml
# configs/mooring_iteration_advanced.yml

iteration:
  method: "newton_raphson"

  convergence:
    tolerance: 0.5
    min_tolerance: 0.2
    max_iterations: 100
    damping_factor: 0.5       # More conservative

  jacobian:
    perturbation_factor: 0.002
    min_perturbation: 0.5
    cache_enabled: true
    recompute_interval: 5     # Recompute every N iterations

  vessel_config:
    fix_vessels: true
    vessels_to_fix: ["Buoy"]
    fix_degrees_of_freedom: ["X", "Y", "Rotation 3"]

  ea_config:                  # For EA-based method
    stiffness_factor: 1.0
    length_limit_factor: 0.1  # Max 10% length change per iteration

lines:
  - name: "Chain_Segment_1"
    target_tension: 500.0
    tolerance: 0.5
    variable_section: 0
    min_length: 50.0          # Minimum allowable length
    max_length: 200.0         # Maximum allowable length
    ea_value: 1.5e9           # Axial stiffness (N)

  - name: "Wire_Segment_1"
    target_tension: 1200.0
    tolerance: 0.5
    variable_section: 1
    min_length: 100.0
    max_length: 500.0
    ea_value: 2.8e9
```
