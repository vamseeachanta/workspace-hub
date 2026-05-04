---
name: orcaflex-modeling-vessel-loading
description: 'Sub-skill of orcaflex-modeling: Vessel Loading (+1).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Vessel Loading (+1)

## Vessel Loading


Load vessel data from external sources.

```yaml
orcaflex:
  preprocess:
    VesselType_Loading:
      flag: true
      source: "vessel_database.csv"
      vessel_name: "FPSO_Alpha"
```

## YAML Validation


Check model configuration before running.

```yaml
orcaflex:
  preprocess:
    check_yml_file:
      flag: true
      strict: true
      report_path: "logs/validation_report.txt"
```
