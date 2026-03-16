---
name: marine-safety-incidents-incident-csv
description: 'Sub-skill of marine-safety-incidents: Incident CSV (+1).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Incident CSV (+1)

## Incident CSV


```csv
incident_id,date,location_lat,location_lon,vessel_type,incident_type,severity,fatalities,injuries,source
INC001,2023-05-15,28.5,-88.2,tanker,collision,high,0,3,uscg
INC002,2023-06-20,29.1,-94.5,platform,fire,critical,2,5,bsee
```

## Risk Assessment JSON


```json
{
  "assessment_date": "2024-01-15",
  "vessel_type": "offshore_platform",
  "region": "gulf_of_mexico",
  "overall_risk_score": 7.2,
  "risk_level": "HIGH",
  "factors": {
    "historical_incidents": 8.5,
    "weather_exposure": 6.0,

*See sub-skills for full details.*
