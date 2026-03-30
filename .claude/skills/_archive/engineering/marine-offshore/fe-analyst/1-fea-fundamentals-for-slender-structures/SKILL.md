---
name: fe-analyst-1-fea-fundamentals-for-slender-structures
description: 'Sub-skill of fe-analyst: 1. FEA Fundamentals for Slender Structures.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. FEA Fundamentals for Slender Structures

## 1. FEA Fundamentals for Slender Structures


OrcaFlex models slender structures (pipes, lines, cables) as **Euler-Bernoulli beam elements** with:

| DOF per node | Description |
|---|---|
| u, v, w | Translational (surge, sway, heave) |
| θx, θy, θz | Rotational (roll, pitch, yaw) |

**Element stiffness contributions**:
- Axial stiffness: `EA` (axial force vs. extension)
- Bending stiffness: `EI` (moment vs. curvature)
- Torsional stiffness: `GJ` (torque vs. twist)
- Shear stiffness: optional (Timoshenko)

**Key non-linearities** in slender structure FEA:
- Geometric non-linearity (large displacements, catenary shape)
- Contact non-linearity (seabed, bend stiffeners, clamps)
- Material non-linearity (yield — typically not modelled for fatigue)
- Hydrodynamic drag non-linearity (Morison equation, velocity-squared)

---
