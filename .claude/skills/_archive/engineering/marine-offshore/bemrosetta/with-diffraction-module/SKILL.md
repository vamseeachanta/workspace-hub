---
name: bemrosetta-with-diffraction-module
description: 'Sub-skill of bemrosetta: With diffraction module (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# With diffraction module (+1)

## With diffraction module


```python
from digitalmodel.diffraction import OrcaFlexExporter
from digitalmodel.bemrosetta import AQWAParser

# BEMRosetta uses diffraction module schemas
parser = AQWAParser()
results = parser.parse("analysis.LIS")  # Returns DiffractionResults

# Can use existing OrcaFlexExporter
exporter = OrcaFlexExporter(results, output_dir)
exporter.export_all()
```

## With hydrodynamics module


```python
from digitalmodel.hydrodynamics import CoefficientDatabase

# Store parsed coefficients in database
db = CoefficientDatabase()
db.store(results.added_mass, results.damping)
```
