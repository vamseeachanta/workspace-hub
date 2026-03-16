---
name: doc-extraction-naval-architecture-source-code-alignment
description: 'Sub-skill of doc-extraction-naval-architecture: Source Code Alignment.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Source Code Alignment

## Source Code Alignment


Extracted data should align with existing module structures:

| Module | Path | Relevant data |
|--------|------|---------------|
| Parametric hull | `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/parametric_hull.py` | Hull dimensions, form coefficients |
| Hydrostatics report | `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_builders_hydrostatics.py` | GM, BM, KB, centre of buoyancy, waterplane area |
