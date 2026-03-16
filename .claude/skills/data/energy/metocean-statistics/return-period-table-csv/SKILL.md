---
name: metocean-statistics-return-period-table-csv
description: 'Sub-skill of metocean-statistics: Return Period Table (CSV) (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Return Period Table (CSV) (+2)

## Return Period Table (CSV)


```csv
return_period_years,Hs_m,Hs_lower_CI,Hs_upper_CI,Tp_s,Tp_lower_CI,Tp_upper_CI,U10_ms,U10_lower_CI,U10_upper_CI
1,5.2,4.8,5.6,10.5,9.8,11.2,18.3,16.9,19.7
2,6.1,5.6,6.6,11.2,10.4,12.0,20.5,18.9,22.1
5,7.1,6.5,7.7,11.8,10.9,12.7,22.1,20.3,23.9
10,7.8,7.1,8.5,12.1,11.2,13.0,23.4,21.4,25.4
25,8.7,7.9,9.5,12.6,11.6,13.6,25.2,23.0,27.4
50,9.4,8.4,10.4,13.2,12.1,14.3,27.1,24.7,29.5
100,10.2,9.0,11.4,13.8,12.6,15.0,28.9,26.2,31.6
500,12.1,10.5,13.7,15.1,13.7,16.5,32.4,29.2,35.6
```

## Summary Statistics (JSON)


```json
{
  "parameter": "wave_height_m",
  "unit": "m",
  "period": {
    "start": "2014-01-01",
    "end": "2024-12-31",
    "years": 11
  },
  "statistics": {

*See sub-skills for full details.*

## Directional Statistics (JSON)


```json
{
  "parameter": "wave_height_m",
  "sectors": 8,
  "convention": "direction_from",
  "data": [
    {"direction": 0, "label": "N", "mean": 1.2, "max": 5.4, "p90": 2.1, "occurrence_pct": 8.2},
    {"direction": 45, "label": "NE", "mean": 1.4, "max": 6.1, "p90": 2.4, "occurrence_pct": 12.5},
    {"direction": 90, "label": "E", "mean": 1.1, "max": 4.8, "p90": 1.9, "occurrence_pct": 9.8},
    {"direction": 135, "label": "SE", "mean": 0.9, "max": 4.2, "p90": 1.6, "occurrence_pct": 7.1},

*See sub-skills for full details.*
