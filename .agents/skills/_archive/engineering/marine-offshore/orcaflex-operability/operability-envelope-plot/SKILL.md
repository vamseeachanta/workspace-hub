---
name: orcaflex-operability-operability-envelope-plot
description: 'Sub-skill of orcaflex-operability: Operability Envelope Plot (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Operability Envelope Plot (+2)

## Operability Envelope Plot


Interactive Plotly polar plot showing:
- Maximum tension vs heading angle
- Intact and damaged limit circles
- Color-coded utilization zones
- Hover tooltips with exact values

## Critical Headings Table


| Rank | Heading (°) | Max Tension (kN) | Utilization (%) | Critical Line | Status |
|------|-------------|------------------|-----------------|---------------|--------|
| 1 | 45 | 2450.2 | 98.0 | Leg_1 | WARNING |
| 2 | 135 | 2380.5 | 95.2 | Leg_3 | OK |
| 3 | 225 | 2350.1 | 94.0 | Leg_5 | OK |

## Weather Downtime Summary


```json
{
  "annual_downtime_percent": 12.5,
  "operational_hours_per_year": 7665,
  "downtime_hours_per_year": 1095,
  "downtime_days_per_year": 45.6,
  "seasonal_breakdown": {
    "winter": {"downtime_percent": 25.3, "days": 23.1},
    "spring": {"downtime_percent": 10.2, "days": 9.3},
    "summer": {"downtime_percent": 5.1, "days": 4.7},
    "autumn": {"downtime_percent": 9.4, "days": 8.5}
  }
}
```
