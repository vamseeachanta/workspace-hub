---
name: oil-and-gas-volumetrics
description: 'Sub-skill of oil-and-gas: Volumetrics (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Volumetrics (+3)

## Volumetrics


```python
# Stock Tank Oil Initially In Place (STOIIP)
STOIIP = 7758 * A * h * phi * (1 - Sw) / Boi   # STB

# Gas Initially In Place (GIIP)
GIIP = 43560 * A * h * phi * (1 - Sw) / Bgi    # SCF
```

## Decline Curves


```python
import numpy as np

# Exponential decline
q_exp = qi * np.exp(-D * t)

# Hyperbolic decline
q_hyp = qi / (1 + b * D * t) ** (1 / b)

# Harmonic decline (b = 1)
q_harm = qi / (1 + D * t)
```

## Material Balance (General Form)


```python
# F = N * Et + We - Wp * Bw
# F  = underground withdrawal
# Et = total expansion
# We = water influx
```

## STOIIP Function with Validation


```python
def calculate_oil_in_place(
    area_acres: float,
    thickness_ft: float,
    porosity: float,
    water_saturation: float,
    formation_volume_factor: float
) -> float:
    """
    Calculate Stock Tank Oil Initially In Place (STOIIP).

*See sub-skills for full details.*
