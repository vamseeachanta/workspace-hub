---
name: orcaflex-extreme-analysis-linked-statistics-csv
description: 'Sub-skill of orcaflex-extreme-analysis: Linked Statistics CSV (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Linked Statistics CSV (+1)

## Linked Statistics CSV


```csv
File,Primary_Object,Primary_Variable,Max,Min,TimeOfMax,TimeOfMin,Heave_AtMax,Pitch_AtMax,Roll_AtMax,Heave_AtMin,Pitch_AtMin,Roll_AtMin
case_001,Mooring_Line_1,Effective Tension,2450.5,320.1,1823.4,2156.7,3.2,-1.5,0.8,-2.1,0.9,-0.3
case_002,Mooring_Line_1,Effective Tension,2380.2,345.6,1567.2,1890.3,2.8,-1.2,0.5,-1.8,0.7,-0.2
```

## Extreme Summary Report


```json
{
  "simulation": "mooring_100yr.sim",
  "primary": {
    "object": "Mooring_Line_1",
    "variable": "Effective Tension",
    "units": "kN"
  },
  "extremes": {
    "maximum": {

*See sub-skills for full details.*
