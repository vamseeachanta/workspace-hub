---
name: orcaflex-installation-analysis-reference-elevation-file
description: 'Sub-skill of orcaflex-installation-analysis: Reference Elevation File
  (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Reference Elevation File (+2)

## Reference Elevation File


Contains the initial Z positions for all objects:

```yaml
# models/elevation_reference.yml

6DBuoys:
  Subsea_Structure:
    InitialZ: -50.0      # Initial elevation
    InitialRotation3: 45  # Initial rotation (deg)


*See sub-skills for full details.*

## Delta Elevation Application


For each `delta_elevation`:
1. **6DBuoys**: `NewZ = ReferenceZ + delta_elevation`
2. **3DBuoys**: `NewZ = ReferenceZ + delta_elevation`
3. **Line EndBZ**: `NewEndBZ = ReferenceEndBZ + delta_elevation`
4. **Line Length**: `NewLength = ReferenceLength + |delta_elevation|`

## Crane Wire Extension


As structure lowers, crane wire extends:

```python
# For each delta_elevation
new_wire_length = reference_length + abs(delta_elevation)
```
