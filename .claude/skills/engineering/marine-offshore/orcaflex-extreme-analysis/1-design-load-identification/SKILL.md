---
name: orcaflex-extreme-analysis-1-design-load-identification
description: 'Sub-skill of orcaflex-extreme-analysis: 1. Design Load Identification
  (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Design Load Identification (+2)

## 1. Design Load Identification


```python
# Find maximum tension for structural design
config = {
    "primary": {"object": "Riser", "variable": "Wall Tension"},
    "linked": [
        {"object": "Riser", "variable": "Curvature"},
        {"object": "Riser", "variable": "Bend Moment"}
    ]
}

results = extractor.extract_linked_statistics(sim_file, config)
design_tension = results["Max"] * 1.1  # Add 10% margin
```

## 2. VIV Characterization


```python
# Characterize conditions at maximum amplitude
config = {
    "primary": {"object": "Riser", "variable": "Max Amplitude"},
    "linked": [
        {"object": "Environment", "variable": "Current Velocity"},
        {"object": "Riser", "variable": "Inline Frequency"}
    ]
}
```

## 3. Mooring Load Case


```python
# Extract design load case for mooring
config = {
    "primary": {"object": "Hawser", "variable": "Effective Tension"},
    "linked": [
        {"object": "Tanker", "variable": "X"},
        {"object": "Tanker", "variable": "Y"},
        {"object": "Tanker", "variable": "Heading"}
    ]
}

# Results define the design load case
```
