---
name: ship-dynamics-6dof-3-natural-frequencies-and-periods
description: 'Sub-skill of ship-dynamics-6dof: 3. Natural Frequencies and Periods
  (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 3. Natural Frequencies and Periods (+1)

## 3. Natural Frequencies and Periods


**Uncoupled Natural Frequency:**
```python
def calculate_natural_frequency_uncoupled(
    mass: float,
    stiffness: float
) -> dict:
    """
    Calculate natural frequency for single DOF.

    ω_n = sqrt(K / M)
    T_n = 2π / ω_n

    Args:
        mass: Mass or moment of inertia
        stiffness: Stiffness or restoring coefficient

    Returns:
        Natural frequency and period
    """
    omega_n = np.sqrt(stiffness / mass)
    period_n = 2 * np.pi / omega_n
    frequency_hz = omega_n / (2 * np.pi)

    return {
        'omega_rad_s': omega_n,
        'frequency_hz': frequency_hz,
        'period_s': period_n
    }

# Example: Heave natural period
m = 150000 * 1000  # kg
A33 = 50000 * 1000  # Added mass in heave (kg)
K33 = 1025 * 9.81 * 15000  # Heave stiffness (N/m)

heave_freq = calculate_natural_frequency_uncoupled(
    mass=m + A33,
    stiffness=K33
)

print(f"Heave natural period: {heave_freq['period_s']:.2f} seconds")
```

**Coupled Natural Frequencies:**
```python
def calculate_coupled_natural_frequencies(
    mass_matrix: np.ndarray,
    stiffness_matrix: np.ndarray
) -> dict:
    """
    Calculate coupled natural frequencies from eigenvalue problem.

    det([K] - ω²[M]) = 0

    Args:
        mass_matrix: 6x6 mass matrix (including added mass)
        stiffness_matrix: 6x6 stiffness matrix

    Returns:
        Natural frequencies for all modes
    """
    # Solve generalized eigenvalue problem
    eigenvalues, eigenvectors = np.linalg.eig(
        np.linalg.solve(mass_matrix, stiffness_matrix)
    )

    # Natural frequencies
    omega_n = np.sqrt(eigenvalues.real)
    periods = 2 * np.pi / omega_n

    # Sort by period
    sort_idx = np.argsort(periods)
    periods = periods[sort_idx]
    omega_n = omega_n[sort_idx]
    eigenvectors = eigenvectors[:, sort_idx]

    dof_names = ['Surge', 'Sway', 'Heave', 'Roll', 'Pitch', 'Yaw']

    return {
        'periods_s': periods,
        'frequencies_rad_s': omega_n,
        'frequencies_hz': omega_n / (2*np.pi),
        'mode_shapes': eigenvectors,
        'dof_names': dof_names
    }

# Example
M_total = M_fpso + np.diag([15000e3, 15000e3, 50000e3, 1e9, 1e9, 5e8])  # With added mass
K = np.diag([0, 0, 150e6, 5e9, 8e9, 0])  # Hydrostatic stiffness

natural_freq = calculate_coupled_natural_frequencies(M_total, K)

print("Natural Periods:")
for i, (dof, T) in enumerate(zip(natural_freq['dof_names'], natural_freq['periods_s'])):
    print(f"  {dof}: {T:.2f} seconds")
```


## 4. Hydrostatic Restoring


**Complete Stiffness Matrix:**
```python
def calculate_complete_hydrostatic_stiffness(
    rho: float,
    g: float,
    displacement: float,
    waterplane_area: float,
    waterplane_inertia: dict,
    center_of_buoyancy: np.ndarray,
    center_of_gravity: np.ndarray,
    metacentric_height: dict
) -> np.ndarray:
    """
    Calculate complete 6x6 hydrostatic stiffness matrix.

    Args:
        rho: Water density (kg/m³)
        g: Gravity (m/s²)
        displacement: Volume displacement (m³)
        waterplane_area: Waterplane area (m²)
        waterplane_inertia: {'Ixx': Ixx, 'Iyy': Iyy} second moments (m⁴)
        center_of_buoyancy: [xb, yb, zb] (m)
        center_of_gravity: [xg, yg, zg] (m)
        metacentric_height: {'GMT': transverse, 'GML': longitudinal} (m)

    Returns:
        6x6 hydrostatic stiffness matrix
    """
    xb, yb, zb = center_of_buoyancy
    xg, yg, zg = center_of_gravity

    C = np.zeros((6, 6))

    # C33: Heave stiffness
    C[2, 2] = rho * g * waterplane_area

    # C44: Roll stiffness
    C[3, 3] = rho * g * displacement * metacentric_height['GMT']

    # C55: Pitch stiffness
    C[4, 4] = rho * g * displacement * metacentric_height['GML']

    # Coupling terms
    # C35, C53: Heave-pitch
    C[2, 4] = -rho * g * waterplane_area * xb
    C[4, 2] = C[2, 4]

    # C34, C43: Heave-roll
    C[2, 3] = -rho * g * waterplane_area * yb
    C[3, 2] = C[2, 3]

    # C45, C54: Roll-pitch
    C[3, 4] = -rho * g * displacement * (zg - zb)
    C[4, 3] = C[3, 4]

    return C

# Example: FPSO hydrostatic stiffness
C_hydro = calculate_complete_hydrostatic_stiffness(
    rho=1025,
    g=9.81,
    displacement=150000,  # m³
    waterplane_area=15000,  # m²
    waterplane_inertia={'Ixx': 5e5, 'Iyy': 3e7},  # m⁴
    center_of_buoyancy=np.array([160, 0, -10]),
    center_of_gravity=np.array([160, 0, 15]),
    metacentric_height={'GMT': 3.0, 'GML': 5.0}
)

print("Hydrostatic Stiffness Matrix (diagonal terms):")
print(np.diag(C_hydro))
```
