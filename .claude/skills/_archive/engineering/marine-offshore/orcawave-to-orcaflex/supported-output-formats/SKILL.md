---
name: orcawave-to-orcaflex-supported-output-formats
description: 'Sub-skill of orcawave-to-orcaflex: Supported Output Formats (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Supported Output Formats (+1)

## Supported Output Formats


| Format | Extension | Use Case |
|--------|-----------|----------|
| YAML | .yml | OrcaFlex vessel type |
| CSV | .csv | Spreadsheet analysis |
| Excel | .xlsx | Multi-sheet export |
| JSON | .json | API integration |
| OrcaFlex Data | .dat | Direct OrcaFlex import |
| HDF5 | .h5 | Large dataset storage |

## Multi-Format Export


```python
from digitalmodel.diffraction.orcawave_converter import OrcaWaveConverter

# Convert and export to multiple formats
converter = OrcaWaveConverter(vessel)
unified_data = converter.convert()

# Export all formats
converter.export_all_formats(
    unified_data,
    output_directory="exports/",
    base_name="fpso_hydro",
    formats=["yaml", "csv", "xlsx", "json"]
)
```
