---
name: hydrodynamic-analysis-3-added-mass-and-damping
description: 'Sub-skill of hydrodynamic-analysis: 3. Added Mass and Damping (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 3. Added Mass and Damping (+1)

## 3. Added Mass and Damping


**Frequency-Dependent Coefficients:**
```python
def interpolate_hydrodynamic_coefficients(
    omega_target: float,
    omega_data: np.ndarray,
    coefficient_data: np.ndarray
) -> np.ndarray:
    """
    Interpolate added mass or damping at target frequency.

    Args:
        omega_target: Target frequency (rad/s)
        omega_data: Frequency data from BEM
        coefficient_data: Coefficient matrix (n_freq x 6 x 6)

    Returns:
        Interpolated 6x6 coefficient matrix
    """
    from scipy.interpolate import interp1d

    # Interpolate each element
    coefficient_interp = np.zeros((6, 6))

    for i in range(6):
        for j in range(6):
            # Extract time series for this coefficient
            coef_series = coefficient_data[:, i, j]

            # Create interpolator
            interpolator = interp1d(
                omega_data,
                coef_series,
                kind='cubic',
                fill_value='extrapolate'
            )

            # Interpolate
            coefficient_interp[i, j] = interpolator(omega_target)

    return coefficient_interp

# Example usage
omega_data = np.array([0.1, 0.5, 1.0, 1.5, 2.0])  # rad/s
added_mass_data = np.random.rand(5, 6, 6) * 10000  # Sample data

# Interpolate at T = 8s (omega = 0.785 rad/s)
A_interp = interpolate_hydrodynamic_coefficients(
    omega_target=2*np.pi/8,
    omega_data=omega_data,
    coefficient_data=added_mass_data
)

print(f"Added mass at T=8s:")
print(A_interp)
```

**Infinite Frequency Added Mass:**
```python
def calculate_infinite_frequency_added_mass(
    omega_data: np.ndarray,
    added_mass_data: np.ndarray
) -> np.ndarray:
    """
    Estimate infinite frequency added mass (A_inf).

    A_inf = lim(ω→∞) A(ω)

    Args:
        omega_data: Frequency array
        added_mass_data: Added mass array (n_freq x 6 x 6)

    Returns:
        6x6 infinite frequency added mass
    """
    # Use highest frequency values and extrapolate
    # Typically: fit A(ω) = A_inf + C/ω²

    A_inf = np.zeros((6, 6))

    for i in range(6):
        for j in range(6):
            # Take average of highest 3 frequencies
            A_inf[i, j] = np.mean(added_mass_data[-3:, i, j])

    return A_inf
```


## 4. Wave Forces


**Froude-Krylov Force:**
```python
def calculate_froude_krylov_force(
    wave_amplitude: float,
    omega: float,
    waterplane_area: float,
    center_of_buoyancy_depth: float,
    rho: float = 1025
) -> float:
    """
    Calculate Froude-Krylov force (undisturbed wave pressure).

    F_FK = ρ g ζ_a A_wp e^(k z_b)

    Args:
        wave_amplitude: Wave amplitude (m)
        omega: Wave frequency (rad/s)
        waterplane_area: Waterplane area (m²)
        center_of_buoyancy_depth: Depth of center of buoyancy (m)
        rho: Water density (kg/m³)

    Returns:
        Froude-Krylov force amplitude (N)
    """
    g = 9.81

    # Wave number (deep water approximation)
    k = omega**2 / g

    # Froude-Krylov force
    F_FK = rho * g * wave_amplitude * waterplane_area * np.exp(k * center_of_buoyancy_depth)

    return F_FK

# Example
F_FK = calculate_froude_krylov_force(
    wave_amplitude=2.0,  # 2m amplitude (Hs = 4m)
    omega=2*np.pi/10,    # 10s period
    waterplane_area=15000,  # m²
    center_of_buoyancy_depth=-10  # 10m below waterline
)

print(f"Froude-Krylov force: {F_FK/1e6:.2f} MN")
```

**Diffraction Force:**
```python
def calculate_diffraction_coefficient(
    diameter: float,
    wavelength: float
) -> float:
    """
    Estimate diffraction coefficient.

    Diffraction important when D/λ > 0.2 (MacCamy-Fuchs)

    Args:
        diameter: Characteristic diameter
        wavelength: Wave length

    Returns:
        Diffraction importance factor
    """
    D_over_lambda = diameter / wavelength

    if D_over_lambda < 0.1:
        regime = "Morison (small body)"
    elif D_over_lambda < 0.2:
        regime = "Transition"
    else:
        regime = "Diffraction (large body)"

    print(f"D/λ = {D_over_lambda:.3f} → {regime}")

    return D_over_lambda

# Example: FPSO hull
D = 58  # Beam = 58m
T = 10  # Wave period
wavelength = 9.81 * T**2 / (2 * np.pi)  # Deep water

diffraction_coef = calculate_diffraction_coefficient(D, wavelength)
```
