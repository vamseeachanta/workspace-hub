---
name: file-taxonomy-format-guide
description: 'Sub-skill of file-taxonomy: Format Guide.'
version: 1.6.0
category: workspace
type: reference
scripts_exempt: true
---

# Format Guide

## Format Guide


| Use case | Format | Reason |
|----------|--------|--------|
| Structured config / schema | **YAML** | Human-readable, comment-friendly |
| API responses / machine data | **JSON** | Strict types, universal tooling |
| Tabular data (large) | **CSV** | Pandas-native, Excel-compatible |
| Tabular data (small, typed) | **YAML** | Inline, readable with units |
| Reports (human) | **HTML** or **Markdown** | Browsable / diffable |
| Binary data / matrices | **NumPy .npy** | Efficient, lossless |
| Geospatial | **GeoJSON** or **NetCDF** | Standard for domain |
| Model parameters | **YAML** | Editable, diffable |
| Hydrodynamic output | **.owd** (internal) | OrcaWave native; never convert to CSV |
