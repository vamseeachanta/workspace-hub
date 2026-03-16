---
name: orcaflex-extreme-analysis-basic-extreme-extraction
description: 'Sub-skill of orcaflex-extreme-analysis: Basic Extreme Extraction (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Basic Extreme Extraction (+1)

## Basic Extreme Extraction


```yaml
# configs/extreme_analysis.yml

orcaflex:
  postprocess:
    linked_statistics:
      flag: true

      # Primary variable (extremes will be found for this)
      primary:
        object: "Mooring_Line_1"
        variable: "Effective Tension"

      # Linked variables (values at primary's extremes)
      linked:
        - object: "Vessel"
          variable: "Heave"
        - object: "Vessel"
          variable: "Pitch"
        - object: "Vessel"
          variable: "Roll"
        - object: "Vessel"
          variable: "X"

      # Statistics to extract
      statistics:
        - "Max"
        - "Min"
        - "TimeOfMax"
        - "TimeOfMin"
        - "LinkedValueAtMax"
        - "LinkedValueAtMin"

      output:
        format: csv
        directory: "results/extremes/"
```


## Multi-Object Analysis


```yaml
# configs/extreme_multi_object.yml

orcaflex:
  postprocess:
    linked_statistics:
      flag: true

      # Analyze multiple primary objects
      groups:
        - name: "mooring_tensions"
          primaries:
            - object: "Leg_1"
              variable: "Effective Tension"
            - object: "Leg_2"
              variable: "Effective Tension"
            - object: "Leg_3"
              variable: "Effective Tension"
          linked:
            - object: "CALM_Buoy"
              variable: "X"
            - object: "CALM_Buoy"
              variable: "Y"

        - name: "vessel_motions"
          primaries:
            - object: "Tanker"
              variable: "Heave"
            - object: "Tanker"
              variable: "Pitch"
          linked:
            - object: "Hawser"
              variable: "Effective Tension"

      output:
        format: csv
        directory: "results/extremes/"
        separate_files: true
```
