---
name: orcaflex-extreme-analysis-linked-statistics
description: 'Sub-skill of orcaflex-extreme-analysis: Linked Statistics (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Linked Statistics (+1)

## Linked Statistics


Linked statistics capture what other variables were doing when a primary variable reached its extreme:

```
At time T_max when Line1.Tension = MAX:
  - Vessel.Heave = ?
  - Vessel.Pitch = ?
  - Line1.Curvature = ?
  - Wave.Elevation = ?
```

This enables understanding of the physical conditions that caused the extreme.

## Extreme Types


| Statistic | Description |
|-----------|-------------|
| `Max` | Maximum value during simulation |
| `Min` | Minimum value during simulation |
| `TimeOfMax` | Time when maximum occurred |
| `TimeOfMin` | Time when minimum occurred |
| `ValueAtMax` | Primary variable's max value |
| `ValueAtMin` | Primary variable's min value |
| `LinkedValueAtMax` | Secondary variable value at primary's max time |
| `LinkedValueAtMin` | Secondary variable value at primary's min time |
