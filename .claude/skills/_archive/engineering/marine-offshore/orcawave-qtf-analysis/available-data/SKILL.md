---
name: orcawave-qtf-analysis-available-data
description: 'Sub-skill of orcawave-qtf-analysis: Available Data (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Available Data (+1)

## Available Data


```python
# Mean drift loads (3 methods available)
mean_drift_pressure = model.meanDriftLoadPressureIntegration
mean_drift_momentum = model.meanDriftLoadMomentumConservation
mean_drift_control = model.meanDriftLoadControlSurface

# QTF data structure
qtf_freqs = model.QTFFrequencies
qtf_periods = model.QTFPeriods
qtf_heading_pairs = model.QTFHeadingPairs

*See sub-skills for full details.*

## Heading Pair Management


```python
from digitalmodel.orcawave.qtf import QTFHeadingManager

# Manage QTF heading pairs
manager = QTFHeadingManager()

# Define heading pairs for bi-directional seas
pairs = manager.generate_pairs(
    headings=[0, 30, 60, 90, 120, 150, 180],
    pair_type="symmetric"  # Reduce computation using symmetry

*See sub-skills for full details.*
