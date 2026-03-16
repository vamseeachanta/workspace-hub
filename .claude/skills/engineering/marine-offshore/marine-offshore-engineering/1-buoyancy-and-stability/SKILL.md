---
name: marine-offshore-engineering-1-buoyancy-and-stability
description: 'Sub-skill of marine-offshore-engineering: 1. Buoyancy and Stability
  (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Buoyancy and Stability (+1)

## 1. Buoyancy and Stability


```python
def calculate_metacentric_height(
    displacement: float,  # tonnes
    waterplane_area: float,  # m²
    center_of_buoyancy_height: float,  # m
    center_of_gravity_height: float  # m
) -> float:
    """
    Calculate metacentric height (GM) for stability.

    GM = KB + BM - KG

    Where:
    - KB = Center of buoyancy above keel
    - BM = Metacentric radius = I/V
    - KG = Center of gravity above keel

    Args:
        displacement: Vessel displacement
        waterplane_area: Area at waterline
        center_of_buoyancy_height: KB
        center_of_gravity_height: KG

    Returns:
        Metacentric height in meters
    """
    rho = 1.025  # t/m³
    volume = displacement / rho

    # Second moment of area (simplified for rectangular waterplane)
    I = waterplane_area**1.5 / 12  # Approximation

    # Metacentric radius
    BM = I / volume

    # Metacentric height
    GM = center_of_buoyancy_height + BM - center_of_gravity_height

    return GM
```


## 2. Riser Stress


```python
def calculate_riser_stress(
    top_tension: float,  # kN
    weight_per_length: float,  # kg/m
    water_depth: float,  # m
    diameter: float,  # mm
    wall_thickness: float  # mm
) -> dict:
    """
    Calculate riser stresses.

    Args:
        top_tension: Top tension
        weight_per_length: Riser weight in water
        water_depth: Water depth
        diameter: Outer diameter
        wall_thickness: Wall thickness

    Returns:
        Stress components
    """
    # Cross-sectional area
    D_outer = diameter / 1000  # Convert to m
    D_inner = D_outer - 2 * wall_thickness / 1000
    A = np.pi * (D_outer**2 - D_inner**2) / 4  # m²

    # Effective tension at bottom
    w = weight_per_length * 9.81 / 1000  # kN/m
    bottom_tension = top_tension - w * water_depth

    # Axial stress (top)
    sigma_axial_top = top_tension * 1000 / (A * 1e6)  # MPa

    # Axial stress (bottom)
    sigma_axial_bottom = bottom_tension * 1000 / (A * 1e6)  # MPa

    return {
        'top_stress_MPa': sigma_axial_top,
        'bottom_stress_MPa': sigma_axial_bottom,
        'bottom_tension_kN': bottom_tension
    }
```
