---
name: ship-dynamics-6dof-1-6-degrees-of-freedom
description: 'Sub-skill of ship-dynamics-6dof: 1. 6 Degrees of Freedom (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. 6 Degrees of Freedom (+1)

## 1. 6 Degrees of Freedom


**DOF Definition:**
```yaml
translations:
  surge:    # X-direction (longitudinal)
    positive: "Forward"
    typical_natural_period: "50-150 seconds"

  sway:     # Y-direction (lateral)
    positive: "Port"
    typical_natural_period: "50-150 seconds"

  heave:    # Z-direction (vertical)
    positive: "Upward"
    typical_natural_period: "6-15 seconds"

rotations:
  roll:     # Rotation about X-axis
    positive: "Starboard down"
    typical_natural_period: "15-30 seconds"

  pitch:    # Rotation about Y-axis
    positive: "Bow up"
    typical_natural_period: "6-12 seconds"

  yaw:      # Rotation about Z-axis
    positive: "Bow to starboard"
    typical_natural_period: "60-200 seconds"
```


## 2. Equations of Motion


**General Form:**
```
[M + A(ω)]{ẍ} + [B(ω)]{ẋ} + [C]{x} = {F(t)}

Where:
- [M] = Mass/inertia matrix (6x6)
- [A] = Added mass matrix (6x6, frequency-dependent)
- [B] = Damping matrix (6x6, frequency-dependent)
- [C] = Hydrostatic restoring matrix (6x6)
- {F} = External force vector (6x1)
- {x} = Displacement vector [surge, sway, heave, roll, pitch, yaw]
```

**Mass Matrix:**
```python
import numpy as np

def create_mass_matrix(
    mass: float,
    radii_of_gyration: dict,
    center_of_gravity: np.ndarray = None
) -> np.ndarray:
    """
    Create 6x6 mass matrix for vessel.

    Args:
        mass: Vessel mass (tonnes)
        radii_of_gyration: {'Rxx': roll, 'Ryy': pitch, 'Rzz': yaw} (m)
        center_of_gravity: [x, y, z] from origin (m)

    Returns:
        6x6 mass matrix
    """
    if center_of_gravity is None:
        center_of_gravity = np.zeros(3)

    xg, yg, zg = center_of_gravity

    # Convert to kg
    m = mass * 1000

    # Moments of inertia
    Ixx = m * radii_of_gyration['Rxx']**2  # Roll
    Iyy = m * radii_of_gyration['Ryy']**2  # Pitch
    Izz = m * radii_of_gyration['Rzz']**2  # Yaw

    # Mass matrix (including CG offset coupling)
    M = np.array([
        [m,  0,  0,    0,      m*zg,  -m*yg],
        [0,  m,  0,   -m*zg,   0,      m*xg],
        [0,  0,  m,    m*yg,  -m*xg,   0   ],
        [0, -m*zg, m*yg,  Ixx,    0,     0   ],
        [m*zg, 0, -m*xg,  0,     Iyy,    0   ],
        [-m*yg, m*xg, 0,  0,      0,     Izz ]
    ])

    return M

# Example: FPSO mass matrix
M_fpso = create_mass_matrix(
    mass=150000,  # tonnes
    radii_of_gyration={
        'Rxx': 22,   # Roll radius of gyration
        'Ryy': 95,   # Pitch radius of gyration
        'Rzz': 95    # Yaw radius of gyration
    },
    center_of_gravity=np.array([160, 0, 15])  # From aft perpendicular
)

print("Mass Matrix:")
print(M_fpso)
```
