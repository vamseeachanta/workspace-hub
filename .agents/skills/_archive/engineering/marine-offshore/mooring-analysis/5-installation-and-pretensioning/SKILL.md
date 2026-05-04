---
name: mooring-analysis-5-installation-and-pretensioning
description: 'Sub-skill of mooring-analysis: 5. Installation and Pretensioning (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 5. Installation and Pretensioning (+1)

## 5. Installation and Pretensioning


**Pretension Optimization:**
```python
def calculate_pretension(
    water_depth: float,
    horizontal_distance: float,
    target_touchdown_tension: float,
    weight_per_length: float
) -> dict:
    """
    Calculate required pretension for target touchdown tension.

    Args:
        water_depth: Water depth
        horizontal_distance: Horizontal distance to anchor
        target_touchdown_tension: Desired horizontal tension at seabed
        weight_per_length: Line weight per length

    Returns:
        Required pretension
    """
    # Calculate catenary profile
    a = target_touchdown_tension / weight_per_length

    # Suspended length
    s = catenary_suspended_length(
        water_depth,
        horizontal_distance,
        target_touchdown_tension,
        weight_per_length
    )

    # Top tension
    vertical_load = weight_per_length * water_depth
    pretension = np.sqrt(target_touchdown_tension**2 + vertical_load**2)

    return {
        'pretension_kN': pretension,
        'touchdown_tension_kN': target_touchdown_tension,
        'suspended_length_m': s,
        'catenary_parameter_m': a
    }
```


## 6. Dynamic Analysis Considerations


**Low Frequency Motion:**
```python
def estimate_low_frequency_offset(
    mean_wave_drift: float,  # kN
    mooring_stiffness: float  # kN/m
) -> float:
    """
    Estimate vessel low-frequency offset.

    Simple static approximation:
    offset = Force / Stiffness

    Args:
        mean_wave_drift: Mean wave drift force
        mooring_stiffness: Total horizontal stiffness

    Returns:
        Offset in meters
    """
    return mean_wave_drift / mooring_stiffness

def calculate_mooring_stiffness(
    num_lines: int,
    pretension: float,  # kN per line
    fairlead_depth: float,
    weight_per_length: float,
    line_azimuth: list  # degrees for each line
) -> float:
    """
    Calculate total horizontal mooring stiffness.

    Args:
        num_lines: Number of mooring lines
        pretension: Pretension per line
        fairlead_depth: Depth of fairlead below waterline
        weight_per_length: Weight per unit length
        line_azimuth: Azimuth of each line

    Returns:
        Total horizontal stiffness in kN/m
    """
    # Simplified: K = (T/a) for catenary
    # where a = H/w
    stiffness_per_line = weight_per_length * pretension / fairlead_depth

    # Resolve in each direction
    total_stiffness = 0
    for azimuth in line_azimuth:
        # Component in surge direction
        component = stiffness_per_line * np.cos(np.radians(azimuth))
        total_stiffness += component

    return total_stiffness
```
