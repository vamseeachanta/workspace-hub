---
name: orcaflex-environment-config-wave-types
description: 'Sub-skill of orcaflex-environment-config: Wave Types (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Wave Types (+2)

## Wave Types


| Type | Description | Parameters |
|------|-------------|------------|
| **JONSWAP** | Joint North Sea Wave Project spectrum | Hs, Tp, gamma |
| **Dean Stream** | Non-linear stream function | H, T, order |
| **Ochi-Hubble** | Double-peaked spectrum | Hs1, Tp1, Hs2, Tp2 |
| **Pierson-Moskowitz** | Fully developed sea | Hs, Tp |
| **Torsethaugen** | Combined wind-sea/swell | Hs, Tp |
| **User Defined** | Custom spectrum | S(f) table |

## Current Profile


| Parameter | Description | Units |
|-----------|-------------|-------|
| Surface Speed | Current at water surface | m/s |
| Direction | Current direction | deg |
| Profile Type | Depth variation method | - |
| Depth Points | Depth/speed pairs | m, m/s |

## Wind Parameters


| Parameter | Description | Units |
|-----------|-------------|-------|
| Speed | Reference wind speed | m/s |
| Direction | Wind from direction | deg |
| Height | Reference height | m |
| Profile | Vertical profile type | - |
