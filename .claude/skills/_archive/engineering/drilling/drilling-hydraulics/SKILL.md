---
name: drilling-drilling-hydraulics
description: 'Sub-skill of drilling: Drilling Hydraulics (+5).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Drilling Hydraulics (+5)

## Drilling Hydraulics


```python
# Equivalent Circulating Density (ECD)
ECD = MW + (delta_P_annular / (0.052 * TVD))

# Pressure Loss in Annulus
delta_P = (L * rho * v**2) / (25.8 * (Dh - Dp))

# Bit Hydraulics
HHP = (Q * delta_P_bit) / 1714
HSI = HHP / area_bit
```

## Rate of Penetration


```python
# Bourgoyne-Young Model
ROP = K * exp(a1 + sum(ai * xi))

# Mechanical Specific Energy
MSE = (WOB / area_bit) + (2 * pi * RPM * T) / (60 * area_bit * ROP)
```

## Torque and Drag (Soft String Model)


```python
T = T0 + mu * N * L   # Torque
F = F0 + mu * N * L   # Drag (+ for pulling, - for slack off)
# N is normal force, mu is friction factor
```

## Well Control


```python
# Kill Mud Weight
KMW = original_MW + (SIDPP / (0.052 * TVD))

# Maximum Allowable Annular Surface Pressure
MAASP = (fracture_gradient - MW) * 0.052 * shoe_TVD

# Kick Tolerance
KT = (FG - MW_current) * shoe_TVD / depth_total
```

## Example: ECD Calculation


```python
def calculate_ecd(
    mud_weight_ppg: float,
    annular_pressure_loss_psi: float,
    tvd_ft: float
) -> float:
    """
    Calculate Equivalent Circulating Density.

    Args:

*See sub-skills for full details.*

## Example: Parameter Validation


```python
def validate_drilling_parameters(params: dict) -> None:
    """Validate drilling parameters are within safe ranges."""
    if params['mud_weight'] < params['pore_pressure']:
        raise ValueError("Mud weight below pore pressure — kick risk!")
    if params['mud_weight'] > params['fracture_gradient']:
        raise ValueError("Mud weight above fracture gradient — losses risk!")
    if params['wob'] > params['bit_rating']:
        raise ValueError("WOB exceeds bit rating")
```
