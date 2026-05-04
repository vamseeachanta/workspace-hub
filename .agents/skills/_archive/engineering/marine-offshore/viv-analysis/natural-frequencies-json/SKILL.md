---
name: viv-analysis-natural-frequencies-json
description: 'Sub-skill of viv-analysis: Natural Frequencies JSON (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Natural Frequencies JSON (+1)

## Natural Frequencies JSON


```json
{
  "member_name": "Riser1",
  "n_modes": 5,
  "frequencies": [0.15, 0.42, 0.78, 1.21, 1.72],
  "periods": [6.67, 2.38, 1.28, 0.83, 0.58],
  "boundary_conditions": "tension_controlled",
  "effective_tension": 500000.0
}
```

## VIV Screening Report


```json
{
  "member": "Brace1",
  "natural_frequency_hz": 2.5,
  "shedding_frequency_hz": 0.62,
  "reduced_velocity": 4.94,
  "is_susceptible": true,
  "lock_in_margin": 0.94,
  "safety_factor": 1.02,
  "recommendation": "VIV suppression required"
}
```
