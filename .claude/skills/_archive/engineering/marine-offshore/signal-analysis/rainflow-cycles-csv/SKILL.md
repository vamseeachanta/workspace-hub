---
name: signal-analysis-rainflow-cycles-csv
description: 'Sub-skill of signal-analysis: Rainflow Cycles CSV (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Rainflow Cycles CSV (+2)

## Rainflow Cycles CSV


```csv
range,mean,count,from_stress,to_stress
245.3,125.6,1.0,3.0,248.3
198.7,156.2,1.0,56.8,255.6
167.4,89.3,0.5,5.6,173.0
```

## PSD Output CSV


```csv
frequency_hz,psd_stress,psd_heave,psd_pitch
0.001,1.23e+06,0.0045,0.00012
0.002,2.45e+06,0.0089,0.00024
0.005,5.67e+06,0.0234,0.00056
```

## Summary Statistics JSON


```json
{
  "signal_name": "stress",
  "sample_count": 36000,
  "duration_sec": 3600,
  "statistics": {
    "min": -125.4,
    "max": 456.7,
    "mean": 165.3,
    "std": 89.2,

*See sub-skills for full details.*
