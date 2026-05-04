---
name: orcaflex-mooring-iteration-with-mooring-design
description: 'Sub-skill of orcaflex-mooring-iteration: With Mooring Design (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# With Mooring Design (+1)

## With Mooring Design


```python
# 1. Design mooring using mooring-design skill
# 2. Generate initial OrcaFlex model
# 3. Run tension iteration to achieve pretensions
# 4. Verify with dynamic analysis

from digitalmodel.orcaflex.mooring_tension_iteration import MooringTensionIterator
from digitalmodel.orcaflex.universal import UniversalOrcaFlexRunner

# Step 1: Iterate to target tensions

*See sub-skills for full details.*

## With CALM Buoy Analysis


```python
# For CALM buoy mooring systems
config = IterationConfig(
    method="scipy",
    vessel_config=VesselConfig(
        fix_vessels=True,
        vessels_to_fix=["CALM_Buoy"],
        fix_degrees_of_freedom=["X", "Y", "Rotation 3"]
    ),
    lines=[

*See sub-skills for full details.*
