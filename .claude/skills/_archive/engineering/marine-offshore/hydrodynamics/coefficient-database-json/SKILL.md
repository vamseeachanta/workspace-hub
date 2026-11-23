---
name: hydrodynamics-coefficient-database-json
description: 'Sub-skill of hydrodynamics: Coefficient Database JSON (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Coefficient Database JSON (+1)

## Coefficient Database JSON


```json
{
  "vessel_name": "FPSO",
  "frequencies_rad_s": [0.1, 0.2, 0.3],
  "added_mass": {
    "0.1": [[1.2e6, 0, 0, 0, 1.5e7, 0], ...],
    "0.2": [[1.1e6, 0, 0, 0, 1.4e7, 0], ...]
  },
  "damping": {
    "0.1": [[2.5e5, 0, 0, 0, 3.2e6, 0], ...],
    "0.2": [[2.8e5, 0, 0, 0, 3.5e6, 0], ...]
  }
}
```

## Wave Spectrum CSV


```csv
frequency_rad_s,frequency_hz,period_s,spectral_density
0.314,0.050,20.0,0.123
0.628,0.100,10.0,2.456
0.942,0.150,6.67,1.234
```
