---
name: orcaflex-line-wizard-common-line-setup-properties
description: 'Sub-skill of orcaflex-line-wizard: Common Line Setup Properties (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Common Line Setup Properties (+1)

## Common Line Setup Properties


| Property | Description | Values |
|----------|-------------|--------|
| `LineSetupIncluded` | Include in wizard | "Yes", "No" |
| `LineSetupTargetVariable` | What to target | "Tension", "Length" |
| `LineSetupLineEnd` | Where to measure | "End A", "End B" |
| `LineSetupTargetValue` | Target value | kN or m |

## Line Type Properties


| Property | Description | Units |
|----------|-------------|-------|
| `OD` | Outer diameter | m |
| `ID` | Inner diameter | m |
| `MassPerUnitLength` | Mass in air | kg/m |
| `EA` | Axial stiffness | N |
| `EI` | Bending stiffness | N.m² |
| `GJ` | Torsional stiffness | N.m² |
| `Cdx` | Drag coefficient (axial) | - |
| `Cdn` | Drag coefficient (normal) | - |
| `Cmx` | Added mass coeff (axial) | - |
| `Cmn` | Added mass coeff (normal) | - |
