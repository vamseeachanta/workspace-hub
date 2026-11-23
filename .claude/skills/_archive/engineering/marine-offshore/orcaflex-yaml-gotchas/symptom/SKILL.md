---
name: orcaflex-yaml-gotchas-symptom
description: 'Sub-skill of orcaflex-yaml-gotchas: Symptom (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Symptom (+2)

## Symptom

Semantic validator reports `NorthDirection: 0` as "extra" in modular output.


## Root Cause

Builder unconditionally emits `NorthDirection: 0` (default). Monolithic doesn't include it (OrcaFlex assumes 0).


## Fix

Only emit when non-zero:

```python
if sim.north_direction:
    general["NorthDirection"] = sim.north_direction
```
