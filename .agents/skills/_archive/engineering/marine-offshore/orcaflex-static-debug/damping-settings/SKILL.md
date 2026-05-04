---
name: orcaflex-static-debug-damping-settings
description: 'Sub-skill of orcaflex-static-debug: Damping Settings (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Damping Settings (+2)

## Damping Settings


| StaticsDamping | Use Case |
|----------------|----------|
| 1-10 | Well-behaved models |
| 10-50 | Typical offshore models |
| 50-100 | Challenging convergence |
| 100-500 | Severe instabilities |


## Tolerance Settings


| Tolerance | Accuracy | Use Case |
|-----------|----------|----------|
| 1e-6 | Very high | Final production runs |
| 1e-5 | High | Standard analysis |
| 1e-4 | Medium | Initial testing |
| 1e-3 | Low | Debug convergence |


## Iteration Limits


```yaml
general:
  MaxStaticsIterations: 200      # Default is usually 100
  StaticsMinDamping: 0.01
  StaticsMaxDamping: 100
```
