---
name: orcaflex-mooring-iteration-1-scipy-optimization-recommended
description: 'Sub-skill of orcaflex-mooring-iteration: 1. Scipy Optimization (Recommended)
  (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Scipy Optimization (Recommended) (+2)

## 1. Scipy Optimization (Recommended)


Uses `scipy.optimize.fsolve` for robust multi-variable root finding.

**Best for:**
- Well-behaved systems
- Multiple lines with coupling
- Fast convergence

## 2. Newton-Raphson


Multi-dimensional Newton-Raphson with numerical Jacobian.

**Best for:**
- Systems needing fine control
- Cases with known sensitivity
- Debugging convergence issues

## 3. EA-Based (Catenary Theory)


Uses effective axial stiffness from catenary equations.

**Best for:**
- Simple catenary systems
- Initial estimates
- Lightweight iteration
