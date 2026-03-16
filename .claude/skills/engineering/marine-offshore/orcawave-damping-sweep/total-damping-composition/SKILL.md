---
name: orcawave-damping-sweep-total-damping-composition
description: 'Sub-skill of orcawave-damping-sweep: Total Damping Composition (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Total Damping Composition (+1)

## Total Damping Composition


```
Total Damping = Radiation Damping + Viscous Damping + Appendage Damping
                (from OrcaWave)    (user input)      (bilge keels, etc.)
```

## Damping Sources


| Source | Type | Typical Contribution |
|--------|------|---------------------|
| Radiation | Linear | 10-30% of total roll damping |
| Skin friction | Nonlinear | 5-15% |
| Eddy making | Nonlinear | 20-40% |
| Bilge keels | Nonlinear | 40-60% |
| Appendages | Mixed | 5-10% |
