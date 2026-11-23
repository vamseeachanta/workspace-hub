---
name: orcaflex-rao-import-basic-import-configuration
description: 'Sub-skill of orcaflex-rao-import: Basic Import Configuration (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Basic Import Configuration (+1)

## Basic Import Configuration


```yaml
# configs/rao_import.yml

rao_import:
  source:
    type: "aqwa"
    file: "data/hydrodynamics/vessel_aqwa.lis"

  # Target frequency grid
  frequencies:
    min: 0.02    # rad/s
    max: 2.0
    count: 50

  # Target heading grid
  headings:
    values: [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180]
    symmetry: "port_starboard"  # Mirror for 180-360

  # Validation settings
  validation:
    enabled: true
    amplitude_limits:
      surge: 10.0    # m/m
      sway: 10.0
      heave: 5.0
      roll: 50.0     # deg/m
      pitch: 20.0
      yaw: 30.0
    phase_continuity_check: true
    frequency_range_check: true

  # Output
  output:
    format: "orcaflex_yml"
    file: "output/vessel_raos.yml"
```


## Multi-Source Import


```yaml
# configs/rao_multi_import.yml

rao_import:
  sources:
    - name: "full_load"
      type: "aqwa"
      file: "data/vessel_full_load.lis"
      loading_condition: "Full Load"

    - name: "ballast"
      type: "aqwa"
      file: "data/vessel_ballast.lis"
      loading_condition: "Ballast"

  interpolation:
    method: "cubic"
    target_frequencies: "common_grid"
    target_headings: [0, 30, 60, 90, 120, 150, 180]

  output:
    combined_file: "output/vessel_raos_combined.yml"
    separate_files: true
```
