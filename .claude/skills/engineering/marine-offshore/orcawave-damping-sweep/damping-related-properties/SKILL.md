---
name: orcawave-damping-sweep-damping-related-properties
description: 'Sub-skill of orcawave-damping-sweep: Damping-Related Properties.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Damping-Related Properties

## Damping-Related Properties


```python
# Access damping data from OrcaWave model
import OrcFxAPI

model = OrcFxAPI.DiffractionModel("fpso.owr")

# Radiation damping (frequency-dependent)
rad_damping = model.damping  # 6x6xNfreq array

# Extra roll damping (user-specified viscous)

*See sub-skills for full details.*
