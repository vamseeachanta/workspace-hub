---
name: orcaflex-modeling-static-analysis
description: 'Sub-skill of orcaflex-modeling: Static Analysis (+3).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Static Analysis (+3)

## Static Analysis


Quick structural equilibrium check without time-domain simulation.

```yaml
orcaflex:
  analysis:
    static: true
    simulation: false
```

## Dynamic Simulation


Full time-domain hydrodynamic simulation.

```yaml
orcaflex:
  analysis:
    static: false
    simulation: true
```

## Iterative Analysis


Run multiple iterations with parameter variations.

```yaml
orcaflex:
  analysis:
    iterate:
      flag: true
      parameters:
        - name: wave_height
          values: [2.0, 4.0, 6.0, 8.0]
        - name: wave_period
          values: [8, 10, 12]
```

## Mooring Analysis


Specialized mooring system analysis.

```yaml
orcaflex:
  analysis:
    mooring:
      flag: true
      line_types: ["chain", "wire", "polyester"]
      pretension_range: [100, 200, 300]  # kN
```
