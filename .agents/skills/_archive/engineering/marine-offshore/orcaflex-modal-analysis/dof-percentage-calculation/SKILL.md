---
name: orcaflex-modal-analysis-dof-percentage-calculation
description: 'Sub-skill of orcaflex-modal-analysis: DOF Percentage Calculation (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# DOF Percentage Calculation (+2)

## DOF Percentage Calculation


For each mode, the DOF percentage indicates how much of the mode's energy is in each degree of freedom:

```
DOF_percentage = (|max_DOF_value|² / Σ|all_DOF_values|²) × 100
```

## Mode Selection Criteria


A mode is "selected" for a DOF when:
- `DOF_percentage > threshold_percentage`

This filtering helps identify:
- **Heave-dominated modes** (Z threshold)
- **Surge/sway modes** (X/Y threshold)
- **Roll/pitch/yaw modes** (Rotation thresholds)

## Relationship to VIV


Modal frequencies are critical for VIV assessment:

```python
# VIV lock-in check
from digitalmodel.subsea.viv_analysis.viv_analysis import VIVAnalysis

viv = VIVAnalysis()

# Get natural frequency from modal analysis
natural_freq = 1 / mode_period  # Hz

*See sub-skills for full details.*
