---
name: orcaflex-mooring-iteration-scipy-method
description: 'Sub-skill of orcaflex-mooring-iteration: Scipy Method (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Scipy Method (+2)

## Scipy Method


```
1. Define objective function: residual = current_tension - target_tension
2. Optimization variables: line lengths
3. scipy.optimize.fsolve minimizes residuals
4. Length changes distributed across sections proportionally
```

## Newton-Raphson Method


```
1. Calculate Jacobian: J[i,j] = ∂T_i/∂L_j
2. Calculate residuals: r_i = T_current_i - T_target_i
3. Solve: J × ΔL = -r
4. Update: L_new = L_old + damping × ΔL
5. Repeat until convergence
```

## EA-Based Method


```
1. From catenary theory: ΔL ≈ ΔT × L / EA
2. Calculate tension error: ΔT = T_current - T_target
3. Calculate length change: ΔL = ΔT × L / EA
4. Apply with damping
5. Repeat until convergence
```
