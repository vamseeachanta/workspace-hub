---
name: orcawave-qtf-analysis-force-components
description: 'Sub-skill of orcawave-qtf-analysis: Force Components (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Force Components (+1)

## Force Components


| Component | Frequency | Application |
|-----------|-----------|-------------|
| Mean Drift | Zero (DC) | Steady mooring loads |
| Difference-Frequency | Low frequency | Slow drift, resonance |
| Sum-Frequency | High frequency | Springing, ringing |

## Methods


| Method | Accuracy | Computation Time | Use Case |
|--------|----------|------------------|----------|
| Newman Approximation | Moderate | Fast | Initial design |
| Full QTF | High | Slow | Detailed analysis |
| Pressure Integration | High | Moderate | Validation |
| Momentum Conservation | High | Moderate | Deep water |
