---
name: orcaflex-installation-analysis-basic-installation-depth-study
description: 'Sub-skill of orcaflex-installation-analysis: Basic Installation Depth
  Study (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Basic Installation Depth Study (+1)

## Basic Installation Depth Study


```yaml
# configs/installation_config.yml

structure:
  BaseFile: "reference_model.yml"
  reference_model_file: "models/installation_reference.yml"
  reference_elevation_file: "models/elevation_reference.yml"

  # Objects to update
  6DBuoys:
    - "Subsea_Structure"
  3DBuoys:
    - "Masterlink"

  # Lines to extend
  Lines:
    - name: "Crane_Wire"
      EndBZ: true           # Update end B Z coordinate
      length_index: 2       # Section index to extend
      TargetSegmentLength: 5.0
    - name: "Intermediate_Sling"
      EndBZ: true

  # Depth increments from reference
  delta_elevations:
    - 0      # Reference position
    - -10    # 10m below reference
    - -20    # 20m below reference
    - -30    # 30m below reference
    - -50    # 50m below reference
    - -75    # 75m below reference
    - -100   # 100m below reference

Analysis:
  analysis_root_folder: "results/installation/"
```


## Heavy Lift Configuration


```yaml
# configs/heavy_lift_config.yml

reference_elevation_file: "models/heavy_lift_reference.yml"

# Key components
structure: "Topside_Module"
masterlink: "Lifting_Padeye"
crane_wire: "Main_Crane_Wire"
intermediate_sling: "Spreader_Sling"

# Output naming
output_basefile: "topside_installation"

# Installation depths (negative = below reference)
delta_elevations:
  - 0      # At deck level
  - -5     # Splash zone entry
  - -10    # Through splash zone
  - -15    # Below splash zone
  - -20    # Mid-water
  - -30    # Approaching seabed
  - -40    # Near seabed
  - -45    # Final position
```
