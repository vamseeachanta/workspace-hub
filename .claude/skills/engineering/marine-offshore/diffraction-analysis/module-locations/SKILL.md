---
name: diffraction-analysis-module-locations
description: 'Sub-skill of diffraction-analysis: Module Locations.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Module Locations

## Module Locations


```
src/digitalmodel/modules/
├── aqwa/                    # AQWA analysis tools
├── orcawave/                # OrcaWave analysis
├── bemrosetta/              # Format conversion
│   ├── parsers/             # AQWA, QTF parsers
│   ├── converters/          # OrcaFlex export
│   ├── mesh/                # GDF, DAT, STL handlers
│   └── validators/          # Coefficient, causality
├── diffraction/             # Unified schemas
│   ├── output_schemas.py    # DiffractionResults
│   ├── aqwa_converter.py    # AQWA to unified
│   ├── orcawave_converter.py # OrcaWave to unified
│   ├── orcaflex_exporter.py # Export to OrcaFlex
│   └── comparison_framework.py # Compare results
└── hydrodynamics/           # Coefficient database
```
