---
name: fatigue-analysis-1-s-n-curve-fundamentals
description: 'Sub-skill of fatigue-analysis: 1. S-N Curve Fundamentals.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. S-N Curve Fundamentals

## 1. S-N Curve Fundamentals


**S-N Curve Equation:**
```
N = a / (Δσ)^m

Where:
- N = Number of cycles to failure
- Δσ = Stress range
- a = S-N curve constant
- m = Slope of S-N curve (typically 3 for steel, 3-5 for welds)
```

**DNV S-N Curves:**
```python
import numpy as np

def get_dnv_sn_curve(
    curve_class: str,
    thickness: float = 25
) -> dict:
    """
    Get DNV S-N curve parameters.

    DNV-RP-C203 S-N curves:
    - B1: High strength welds, machined
    - C: Good quality welds
    - D: Normal welds
    - E: Rough welds
    - F, F1, F3: Poor quality, notches
    - G: Severe notches
    - W1, W2, W3: Seawater with cathodic protection

    Args:
        curve_class: DNV curve classification
        thickness: Plate thickness (mm) for thickness effect

    Returns:
        S-N curve parameters
    """
    # DNV-RP-C203 Table 2-1
    sn_curves = {
        'B1': {'log_a1': 15.117, 'm1': 4.0, 'log_a2': 17.146, 'm2': 5.0},
        'B2': {'log_a1': 14.885, 'm1': 4.0, 'log_a2': 16.856, 'm2': 5.0},
        'C':  {'log_a1': 12.592, 'm1': 3.0, 'log_a2': 16.320, 'm2': 5.0},
        'C1': {'log_a1': 12.449, 'm1': 3.0, 'log_a2': 16.081, 'm2': 5.0},
        'C2': {'log_a1': 12.301, 'm1': 3.0, 'log_a2': 15.835, 'm2': 5.0},
        'D':  {'log_a1': 12.164, 'm1': 3.0, 'log_a2': 15.606, 'm2': 5.0},
        'E':  {'log_a1': 11.972, 'm1': 3.0, 'log_a2': 15.350, 'm2': 5.0},
        'F':  {'log_a1': 11.699, 'm1': 3.0, 'log_a2': 14.832, 'm2': 5.0},
        'F1': {'log_a1': 11.546, 'm1': 3.0, 'log_a2': 14.576, 'm2': 5.0},
        'F3': {'log_a1': 11.398, 'm1': 3.0, 'log_a2': 14.330, 'm2': 5.0},
        'G':  {'log_a1': 11.245, 'm1': 3.0, 'log_a2': 14.080, 'm2': 5.0},
        'W1': {'log_a1': 11.764, 'm1': 3.0, 'log_a2': 15.091, 'm2': 5.0},
        'W2': {'log_a1': 11.533, 'm1': 3.0, 'log_a2': 14.706, 'm2': 5.0},
        'W3': {'log_a1': 11.262, 'm1': 3.0, 'log_a2': 14.183, 'm2': 5.0}
    }

    if curve_class not in sn_curves:
        raise ValueError(f"Unknown S-N curve class: {curve_class}")

    params = sn_curves[curve_class]

    # Convert log_a to a
    a1 = 10 ** params['log_a1']
    a2 = 10 ** params['log_a2']

    # Thickness correction (ref thickness = 25mm)
    if thickness > 25:
        t_factor = (25 / thickness) ** 0.25
        a1 *= t_factor ** params['m1']
        a2 *= t_factor ** params['m2']

    return {
        'class': curve_class,
        'a1': a1,
        'm1': params['m1'],
        'a2': a2,
        'm2': params['m2'],
        'thickness_mm': thickness
    }

# Example: Get F3 curve for mooring chain
sn_f3 = get_dnv_sn_curve('F3', thickness=127)  # 127mm chain

print(f"S-N Curve F3 (Chain):")
print(f"  a1 = {sn_f3['a1']:.2e}, m1 = {sn_f3['m1']}")
print(f"  a2 = {sn_f3['a2']:.2e}, m2 = {sn_f3['m2']}")
```

**Calculate Cycles to Failure:**
```python
def calculate_cycles_to_failure(
    stress_range: float,
    sn_curve: dict
) -> float:
    """
    Calculate cycles to failure for given stress range.

    N = a / (Δσ)^m

    Args:
        stress_range: Stress range (MPa)
        sn_curve: S-N curve parameters from get_dnv_sn_curve()

    Returns:
        Cycles to failure
    """
    # Use first segment if stress range is high
    # Switch to second segment if N > 1e7 (DNV bi-linear curve)

    N1 = sn_curve['a1'] / (stress_range ** sn_curve['m1'])

    if N1 <= 1e7:
        return N1
    else:
        # Use second segment
        N2 = sn_curve['a2'] / (stress_range ** sn_curve['m2'])
        return N2

# Example
stress_range = 50  # MPa
N = calculate_cycles_to_failure(stress_range, sn_f3)

print(f"Stress range: {stress_range} MPa")
print(f"Cycles to failure: {N:.2e}")
print(f"Years at 1 Hz: {N / (365.25 * 24 * 3600):.2f}")
```
