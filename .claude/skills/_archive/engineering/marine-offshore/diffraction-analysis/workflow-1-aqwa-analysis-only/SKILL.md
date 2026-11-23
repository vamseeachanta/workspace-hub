---
name: diffraction-analysis-workflow-1-aqwa-analysis-only
description: 'Sub-skill of diffraction-analysis: Workflow 1: AQWA Analysis Only (+4).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Workflow 1: AQWA Analysis Only (+4)

## Workflow 1: AQWA Analysis Only


```python
from digitalmodel.aqwa import AQWAAnalysis

# Direct AQWA analysis
analysis = AQWAAnalysis(folder="aqwa_results/")
analysis.run()
```

## Workflow 2: AQWA → OrcaFlex Conversion


```python
from digitalmodel.bemrosetta import (
    AQWAParser, OrcaFlexConverter, validate_coefficients
)

# Parse AQWA
parser = AQWAParser()
results = parser.parse("analysis.LIS")

# Validate

*See sub-skills for full details.*

## Workflow 3: OrcaWave Analysis


```python
from digitalmodel.orcawave import OrcaWaveAnalysis

# Run OrcaWave (requires OrcFxAPI)
analysis = OrcaWaveAnalysis()
analysis.setup_model(vessel_file="vessel.yml")
analysis.run_diffraction()
results = analysis.get_results()
```

## Workflow 4: AQWA vs OrcaWave Comparison


```python
from digitalmodel.diffraction import (
    DiffractionComparator,
    AQWAConverter,
    OrcaWaveConverter,
)

# Convert both sources to unified schema
aqwa_results = AQWAConverter("aqwa_folder/").convert_to_unified_schema()
orcawave_results = OrcaWaveConverter(model).convert_to_unified_schema()

*See sub-skills for full details.*

## Workflow 5: Complete Pipeline with QTF


```python
from digitalmodel.bemrosetta import (
    AQWAParser, QTFParser, OrcaFlexConverter,
    CoefficientValidator, CausalityChecker,
)

# Parse main results
parser = AQWAParser()
results = parser.parse("analysis.LIS")


*See sub-skills for full details.*
