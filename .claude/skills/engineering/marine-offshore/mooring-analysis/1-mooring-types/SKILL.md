---
name: mooring-analysis-1-mooring-types
description: 'Sub-skill of mooring-analysis: 1. Mooring Types (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Mooring Types (+1)

## 1. Mooring Types


**Catenary Mooring:**
```yaml
characteristics:
  restoring_force: "Weight of suspended line"
  typical_water_depth: "< 2000m"
  materials: ["chain", "wire", "combination"]
  advantages:
    - Simple and reliable
    - Well-proven technology
    - Good energy absorption
  disadvantages:
    - Large footprint
    - Heavy at great depths
```

**Taut Mooring:**
```yaml
characteristics:
  restoring_force: "Elastic elongation"
  typical_water_depth: "Any depth"
  materials: ["polyester", "steel wire"]
  advantages:
    - Small footprint
    - Suitable for ultra-deep water
    - Lower weight
  disadvantages:
    - Complex dynamics
    - Requires higher pretension
    - More sensitive to installation
```


## 2. Catenary Equations


**Basic Catenary:**
```python
import numpy as np

def catenary_profile(
    horizontal_tension: float,  # kN
    weight_per_length: float,   # kN/m
    length_on_seabed: float = 0  # m
) -> dict:
    """
    Calculate catenary mooring line profile.

    Catenary equations:
    - x = a * sinh(s/a)
    - z = a * (cosh(s/a) - 1)

    Where a = H/w (catenary parameter)

    Args:
        horizontal_tension: Horizontal tension at touchdown
        weight_per_length: Weight per unit length in water
        length_on_seabed: Length of line on seabed

    Returns:
        Catenary parameters
    """
    # Catenary parameter
    a = horizontal_tension / weight_per_length

    return {
        'catenary_parameter_m': a,
        'horizontal_tension_kN': horizontal_tension,
        'weight_per_length_kN_m': weight_per_length
    }

def catenary_suspended_length(
    water_depth: float,
    horizontal_distance: float,
    horizontal_tension: float,
    weight_per_length: float
) -> float:
    """
    Calculate suspended length of catenary line.

    Solve: z = a(cosh(x/a) - 1) for length s

    Args:
        water_depth: Water depth
        horizontal_distance: Horizontal distance to anchor
        horizontal_tension: Horizontal tension
        weight_per_length: Weight per length

    Returns:
        Suspended line length
    """
    from scipy.optimize import fsolve

    a = horizontal_tension / weight_per_length

    def equations(s):
        # Horizontal: x = a*sinh(s/a)
        # Vertical: z = a*(cosh(s/a) - 1)
        eq1 = a * np.sinh(s/a) - horizontal_distance
        eq2 = a * (np.cosh(s/a) - 1) - water_depth
        return [eq1, eq2]

    # Initial guess
    s0 = np.sqrt(horizontal_distance**2 + water_depth**2)

    # Solve
    solution = fsolve(equations, s0)[0]

    return solution

def catenary_top_tension(
    water_depth: float,
    horizontal_tension: float,
    weight_per_length: float
) -> float:
    """
    Calculate tension at top of catenary line.

    T_top = sqrt(H² + (w*z)²)

    Args:
        water_depth: Water depth
        horizontal_tension: Horizontal tension
        weight_per_length: Weight per length

    Returns:
        Top tension in kN
    """
    vertical_component = weight_per_length * water_depth
    T_top = np.sqrt(horizontal_tension**2 + vertical_component**2)

    return T_top
```
