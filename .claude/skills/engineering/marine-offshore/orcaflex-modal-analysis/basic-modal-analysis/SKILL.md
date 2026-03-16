---
name: orcaflex-modal-analysis-basic-modal-analysis
description: 'Sub-skill of orcaflex-modal-analysis: Basic Modal Analysis (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Basic Modal Analysis (+1)

## Basic Modal Analysis


```yaml
# configs/modal_analysis.yml

default:
  log_level: DEBUG

  Analysis:
    Analyze:
      flag: true
      simulation: false
      statics: false
      modal:
        flag: true
        lastMode: 20              # Number of modes to extract
        mode_shapes: true         # Save full mode shape data
        ObjectName:               # Objects to analyze
          - "Riser1"
          - "Mooring_Line_1"
        dof_analysis:
          dofs:                   # DOFs to filter by
            - "X"
            - "Y"
            - "Z"
            - "Rotation 1"
            - "Rotation 2"
            - "Rotation 3"
          threshold_percentages:  # Filter thresholds
            X: 10.0
            Y: 10.0
            Z: 10.0
            Rotation 1: 10.0
            Rotation 2: 10.0
            Rotation 3: 10.0

Files:
  - Label: "Depth_200m"
    Name: "models/riser_200m.yml"
  - Label: "Depth_500m"
    Name: "models/riser_500m.yml"
```


## Multi-Depth Study


```yaml
# configs/modal_depth_study.yml

default:
  Analysis:
    Analyze:
      modal:
        flag: true
        lastMode: 30
        ObjectName:
          - "SCR"
        dof_analysis:
          dofs: ["Z", "Rotation 1", "Rotation 2"]
          threshold_percentages:
            Z: 15.0
            Rotation 1: 10.0
            Rotation 2: 10.0

Files:
  - Label: "WD_800m"
    Name: "models/scr_wd_800m.yml"
  - Label: "WD_1000m"
    Name: "models/scr_wd_1000m.yml"
  - Label: "WD_1200m"
    Name: "models/scr_wd_1200m.yml"
  - Label: "WD_1500m"
    Name: "models/scr_wd_1500m.yml"
```
