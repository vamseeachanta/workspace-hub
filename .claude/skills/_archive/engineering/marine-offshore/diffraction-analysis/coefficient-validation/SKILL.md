---
name: diffraction-analysis-coefficient-validation
description: 'Sub-skill of diffraction-analysis: Coefficient Validation (+2).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Coefficient Validation (+2)

## Coefficient Validation


- **Symmetry**: Added mass and damping matrices should be symmetric
- **Positive definiteness**: Diagonal elements non-negative
- **Physical limits**: No NaN/Inf values, reasonable magnitudes

## Kramers-Kronig Causality


- Added mass A(ω) and damping B(ω) must satisfy K-K relations
- Tolerance: typically 10% relative error acceptable

## RAO Validation


- Magnitude non-negative
- Phase in reasonable range (-360° to 360°)
- Physical trends (heave RAO → 1.0 at low frequency)
