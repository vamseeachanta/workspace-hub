---
name: orcaflex-rao-import-orcaflex-yaml-format
description: 'Sub-skill of orcaflex-rao-import: OrcaFlex YAML Format (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# OrcaFlex YAML Format (+2)

## OrcaFlex YAML Format


```yaml
VesselTypes:
  - Name: FPSO_RAOs
    DisplacementRAOs:
      RAOOrigin: [150.0, 0.0, 0.0]  # meters from vessel origin
      Directions: [0, 45, 90, 135, 180]  # degrees
      Periods: [5.0, 7.0, 10.0, 12.0, 15.0, 20.0]  # seconds

      # Amplitude and Phase for each DOF
      # Format: [heading][period]

*See sub-skills for full details.*

## DataFrame Export


```python
# Export to DataFrame for analysis
df = processor.to_dataframe(rao_data)

# Multi-level columns: (DOF, Heading)
# Index: Frequency
print(df.head())
#           Surge                    Sway
#           0      45     90        0      45     90
# 0.02      0.95   0.92   0.88     0.02   0.45   0.92
# 0.05      0.92   0.90   0.85     0.05   0.48   0.95
```

## Validation Report


```json
{
  "is_valid": false,
  "issues": [
    {
      "type": "amplitude_exceeded",
      "dof": "roll",
      "heading": 90,
      "frequency": 0.6,
      "value": 55.2,

*See sub-skills for full details.*
