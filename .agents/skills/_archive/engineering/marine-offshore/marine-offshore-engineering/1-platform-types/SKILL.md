---
name: marine-offshore-engineering-1-platform-types
description: 'Sub-skill of marine-offshore-engineering: 1. Platform Types (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Platform Types (+3)

## 1. Platform Types


**Fixed Platforms:**
- **Jacket structures** - Steel lattice framework, common in shallow water (<150m)
- **Jack-ups** - Mobile platforms with retractable legs
- **Compliant towers** - Slender structures for deeper water (300-900m)

**Floating Platforms:**
- **Semi-submersibles** - Pontoons and columns, excellent motion characteristics
- **TLPs (Tension Leg Platforms)** - Vertically moored, minimal vertical motion
- **SPARs** - Deep draft cylindrical hull, good in ultra-deep water
- **FPSOs** - Converted/purpose-built tankers for production and storage

**Selection Criteria:**
```python
def select_platform_type(water_depth: float, field_life: float) -> str:
    """
    Platform type selection based on water depth.

    Args:
        water_depth: Water depth in meters
        field_life: Expected field life in years

    Returns:
        Recommended platform type
    """
    if water_depth < 150:
        return "Fixed platform (Jacket)"
    elif water_depth < 500:
        if field_life < 5:
            return "Jack-up (temporary)"
        else:
            return "Semi-submersible or FPSO"
    elif water_depth < 2000:
        return "Semi-submersible, SPAR, or FPSO"
    else:  # Ultra-deep water
        return "SPAR or FPSO"
```


## 2. Environmental Loading


**Wind Loading:**
- API RP 2A: V = V_1hr * (z/10)^(1/7)  # Wind profile
- Force: F = 0.5 * ρ * V² * Cd * A

**Wave Loading:**
- **Airy (Linear) Wave Theory** - Small amplitude waves
- **Stokes 2nd/3rd Order** - Finite amplitude
- **Stream Function** - Highly nonlinear waves

**Current Loading:**
```python
import numpy as np

def calculate_current_force(
    velocity: float,  # m/s
    diameter: float,   # m
    length: float,     # m
    cd: float = 1.2    # Drag coefficient
) -> float:
    """
    Calculate current force on cylinder.

    Morison equation: F = 0.5 * ρ * V² * Cd * D * L

    Args:
        velocity: Current velocity
        diameter: Member diameter
        length: Member length
        cd: Drag coefficient

    Returns:
        Force in kN
    """
    rho = 1025  # kg/m³ (seawater)
    F = 0.5 * rho * velocity**2 * cd * diameter * length
    return F / 1000  # Convert to kN
```


## 3. Mooring Systems


**Types:**
- **Catenary** - Chain/wire, relies on weight for restoring force
- **Taut** - Polyester/steel wire, high pretension
- **Semi-taut** - Hybrid configuration

**Design Standards:**
- API RP 2SK - Stationkeeping Systems
- DNV-OS-E301 - Position Mooring
- ISO 19901-7 - Stationkeeping Systems

**Safety Factors:**
```yaml
mooring_safety_factors:
  intact:
    uls: 1.67    # Ultimate Limit State
    als: 1.25    # Accidental Limit State
  damaged:
    uls: 1.25
    als: 1.05

  fatigue_design_factor: 10.0
```


## 4. Subsea Systems


**Components:**
- **Subsea trees** - Wellhead control
- **Manifolds** - Production gathering
- **Flowlines** - Fluid transport
- **Risers** - Platform connection
- **Umbilicals** - Control/power/chemical injection

**Pipeline Design:**
```python
def pipeline_wall_thickness(
    diameter: float,  # mm
    pressure: float,  # MPa
    yield_stress: float,  # MPa
    design_factor: float = 0.72  # API 5L
) -> float:
    """
    Calculate required pipeline wall thickness.

    Barlow's formula: t = P*D / (2*σ*F)

    Args:
        diameter: Outer diameter
        pressure: Design pressure
        yield_stress: Material yield stress
        design_factor: Design factor

    Returns:
        Wall thickness in mm
    """
    t = (pressure * diameter) / (2 * yield_stress * design_factor)

    # Add corrosion allowance
    corrosion_allowance = 3.0  # mm
    t_total = t + corrosion_allowance

    return t_total
```
