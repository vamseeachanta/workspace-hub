---
name: cathodic-protection-example-ship-hull-abs-gn-ships-2018
description: 'Sub-skill of cathodic-protection: Example: Ship Hull (ABS GN Ships 2018)
  (+3).'
version: 1.2.0
category: engineering
type: reference
scripts_exempt: true
---

# Example: Ship Hull (ABS GN Ships 2018) (+3)

## Example: Ship Hull (ABS GN Ships 2018)


```python
from digitalmodel.infrastructure.common.cathodic_protection import CathodicProtection

cfg = {
    "inputs": {
        "calculation_type": "ABS_gn_ships_2018",
        "design_data": {
            "design_life": 5,               # years
            "seawater_max_temperature": 20, # Celsius
        },

*See sub-skills for full details.*

## Example: Submarine Pipeline (DNV-RP-F103 2010)


```python
from digitalmodel.infrastructure.common.cathodic_protection import CathodicProtection

cfg = {
    "inputs": {
        "calculation_type": "DNV_RP_F103_2010",
        "design_data": {
            "design_life": 25.0,  # years
        },
        "pipeline": {

*See sub-skills for full details.*

## Example: Offshore Fixed Platform (DNV-RP-B401 2021)


```python
from digitalmodel.infrastructure.common.cathodic_protection import CathodicProtection

cfg = {
    "inputs": {
        "calculation_type": "DNV_RP_B401_offshore",
        "design_data": {
            "design_life": 25.0,           # years
            "structure_type": "jacket",    # jacket | gravity_based | topsides
        },

*See sub-skills for full details.*

## Using router() vs direct method call


```python
# router() dispatches by calculation_type — recommended
result = cp.router(cfg)

# Direct call — same result
cp.ABS_gn_ships_2018(cfg)      # results in cfg["cathodic_protection"]
cp.DNV_RP_F103_2010(cfg)       # results in cfg["results"]
```

Note: ABS route writes to `cfg["cathodic_protection"]`; DNV route writes to `cfg["results"]`.
