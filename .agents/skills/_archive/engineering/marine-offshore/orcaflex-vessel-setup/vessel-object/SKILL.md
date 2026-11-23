---
name: orcaflex-vessel-setup-vessel-object
description: 'Sub-skill of orcaflex-vessel-setup: Vessel Object (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Vessel Object (+1)

## Vessel Object


| Property | Description | Units |
|----------|-------------|-------|
| Name | Unique vessel identifier | - |
| VesselType | Reference to vessel type | - |
| Draught | Operating draft | m |
| InitialPosition | X, Y, Z coordinates | m |
| Orientation | Heading angle | deg |
| Connection | Connection point type | - |

## Vessel Type


| Property | Description | Units |
|----------|-------------|-------|
| Name | Type identifier | - |
| Length | Reference length | m |
| DisplacementRAOs | Motion response operators | m/m, deg/m |
| LoadRAOs | Force response operators | kN/m |
| StiffnessAddedMassDamping | Hydrodynamic coefficients | - |
| QTFs | Quadratic Transfer Functions | - |
