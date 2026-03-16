---
name: orcaflex-modeling-license-check
description: 'Sub-skill of orcaflex-modeling: License Check (+2).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# License Check (+2)

## License Check


```python
from digitalmodel.orcaflex.orcaflex_utilities import OrcaflexUtilities

utils = OrcaflexUtilities()
if utils.is_orcaflex_available():
    print("OrcaFlex license available")
else:
    print("Running in mock mode")
```

## Model Loading


```python
# Load simulation with metadata
model, metadata = utils.get_model_and_metadata("simulation.sim")
print(f"Simulation period: {metadata['period']} seconds")
print(f"Time step: {metadata['timestep']} seconds")
```

## Wave Calculations


```python
# Calculate theoretical maximum wave height
Hmax = utils.get_theoretical_hmax({
    "Hs": 6.0,          # Significant wave height (m)
    "Tp": 12.0,         # Peak period (s)
    "duration": 3600,   # Storm duration (s)
    "gamma": 3.3        # JONSWAP peakedness
})
print(f"Theoretical Hmax: {Hmax:.2f} m")

# Calculate associated period
Tassociated = utils.get_tassociated(Hmax, Tp=12.0)
print(f"Associated period: {Tassociated:.2f} s")
```
