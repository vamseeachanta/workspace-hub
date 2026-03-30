---
name: orcaflex-post-processing-csv-output
description: 'Sub-skill of orcaflex-post-processing: CSV Output (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# CSV Output (+2)

## CSV Output


```csv
Object,Variable,Min,Max,Mean,StdDev,Units
Line1,Effective Tension,450.2,1823.5,892.3,234.1,kN
Line1,Bend Moment,0.0,125.4,45.2,28.9,kN.m
Vessel1,X,-15.2,12.8,-1.2,5.4,m
```

## JSON Output


```json
{
  "simulation": "mooring_case_001.sim",
  "results": [
    {
      "object": "Line1",
      "variable": "Effective Tension",
      "statistics": {
        "min": 450.2,
        "max": 1823.5,

*See sub-skills for full details.*

## Interactive HTML


OPP generates interactive Plotly HTML reports with:
- Zoomable time series
- Hover tooltips with exact values
- Legend toggling
- Export to PNG/SVG
- Responsive design
