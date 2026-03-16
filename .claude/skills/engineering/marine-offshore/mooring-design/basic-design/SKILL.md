---
name: mooring-design-basic-design
description: 'Sub-skill of mooring-design: Basic Design (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Basic Design (+1)

## Basic Design


```python
from mooring_design import (
    MooringSystem, MooringLine, MooringLineProperties,
    AnchorProperties, MooringType, LineType, MooringDesigner
)

# Define line segments
chain = MooringLineProperties(
    line_type=LineType.CHAIN,
    length=400.0,
    diameter=84.0,
    mbl=8500.0,
    weight_water=145.0,
    ea=850000.0
)

# Define anchor
anchor = AnchorProperties(
    anchor_type="suction",
    holding_capacity=5000.0,
    location=(400.0, 0.0, -100.0)
)

# Create mooring line
line1 = MooringLine(
    line_id="ML1",
    segments=[chain],
    anchor=anchor,
    fairlead_location=(20.0, 0.0, -10.0),
    pretension=500.0
)

# Create system
system = MooringSystem(
    system_type=MooringType.CALM,
    water_depth=100.0,
    lines=[line1],  # Add more lines
    vessel_type="tanker"
)

# Analyze
designer = MooringDesigner(system)
results = designer.analyze_intact_condition(
    vessel_offset=(10.0, 5.0, 5.0),
    environment=env
)

for result in results:
    print(f"{result.line_id}: SF={result.safety_factor:.2f} ({'PASS' if result.passes else 'FAIL'})")
```


## Generate OrcaFlex Model


```python
from mooring_design import OrcaFlexModelGenerator

generator = OrcaFlexModelGenerator(system)
generator.generate_model_yml('models/mooring_analysis.yml')
```
