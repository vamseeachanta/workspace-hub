---
name: hydrodynamic-analysis-1-boundary-element-method-bem
description: 'Sub-skill of hydrodynamic-analysis: 1. Boundary Element Method (BEM)
  (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Boundary Element Method (BEM) (+1)

## 1. Boundary Element Method (BEM)


**Potential Flow Theory:**
```
Governing Equation: ∇²φ = 0 (Laplace equation)

Where:
- φ = velocity potential
- Pressure: p = -ρ ∂φ/∂t - ρgz (Bernoulli)
- Velocity: v = ∇φ
```

**BEM Principles:**
```python
def bem_panel_method_concept():
    """
    Conceptual explanation of BEM panel method.

    Key Steps:
    1. Discretize wetted surface into panels
    2. Apply Green's function (source/dipole distribution)
    3. Satisfy boundary conditions on each panel
    4. Solve linear system for unknown potentials
    5. Calculate forces from pressure integration
    """
    pass

# Radiation Problem:
# - Forced oscillation in calm water
# - Calculates added mass and damping
# - 6 DOFs → 6 radiation potentials

# Diffraction Problem:
# - Fixed body in waves
# - Calculates wave excitation forces
# - Different wave headings analyzed
```

**Panel Mesh Quality:**
```yaml
mesh_requirements:
  panel_size:
    general: "< λ/6"  # Lambda = wavelength
    critical_areas: "< λ/10"  # Bow, stern, sharp edges

  aspect_ratio:
    maximum: 3.0
    preferred: 1.5

  panel_count:
    minimum: 2000  # Small vessels
    typical: 5000-10000  # FPSOs
    large: 20000+  # Complex geometries

  symmetry:
    use_if_possible: true  # Reduces computational cost by 50%
    check: "Ensure port-starboard symmetry"
```


## 2. Response Amplitude Operators (RAOs)


**RAO Definition:**
```
RAO(ω) = Response Amplitude / Wave Amplitude

Units:
- Translation (surge, sway, heave): m/m
- Rotation (roll, pitch, yaw): rad/m or deg/m
```

**RAO Calculation:**
```python
import numpy as np

def calculate_rao_from_hydrodynamic_coefficients(
    omega: float,
    mass_matrix: np.ndarray,
    added_mass: np.ndarray,
    damping: np.ndarray,
    stiffness: np.ndarray,
    wave_excitation: np.ndarray
) -> np.ndarray:
    """
    Calculate RAO at frequency omega.

    Equation of motion (frequency domain):
    [-ω²(M + A(ω)) + iω·B(ω) + K]·RAO = F_wave

    Args:
        omega: Wave frequency (rad/s)
        mass_matrix: 6x6 mass matrix
        added_mass: 6x6 added mass matrix at omega
        damping: 6x6 damping matrix at omega
        stiffness: 6x6 hydrostatic stiffness
        wave_excitation: 6x1 complex wave excitation force

    Returns:
        6x1 complex RAO (amplitude and phase)
    """
    # Dynamic stiffness matrix (complex)
    K_dynamic = (
        -omega**2 * (mass_matrix + added_mass) +
        1j * omega * damping +
        stiffness
    )

    # Solve for RAO
    rao_complex = np.linalg.solve(K_dynamic, wave_excitation)

    return rao_complex

# Example: Calculate heave RAO
omega = 2 * np.pi / 10  # T = 10s
M = np.diag([150000, 150000, 150000, 1e7, 1e7, 5e6])  # Mass matrix
A = np.diag([15000, 15000, 50000, 1e6, 1e6, 5e5])     # Added mass
B = np.diag([50000, 50000, 100000, 5e5, 5e5, 2e5])    # Damping
K = np.diag([0, 0, 3000, 0, 0, 0])                    # Hydrostatic stiffness

# Wave excitation (heave dominant)
F_wave = np.array([100000, 0, 500000, 0, 1e6, 0]) + 0j

rao = calculate_rao_from_hydrodynamic_coefficients(omega, M, A, B, K, F_wave)

# Heave RAO amplitude
heave_rao_amplitude = np.abs(rao[2])
heave_rao_phase = np.angle(rao[2], deg=True)

print(f"Heave RAO: {heave_rao_amplitude:.3f} m/m at {heave_rao_phase:.1f}°")
```

**RAO Peak Period:**
```python
def find_rao_peak_period(
    frequencies: np.ndarray,
    rao_amplitude: np.ndarray
) -> dict:
    """
    Find peak RAO period and resonance characteristics.

    Args:
        frequencies: Frequency array (rad/s)
        rao_amplitude: RAO amplitude array

    Returns:
        Peak information
    """
    # Find peak
    peak_idx = np.argmax(rao_amplitude)
    peak_omega = frequencies[peak_idx]
    peak_period = 2 * np.pi / peak_omega
    peak_rao = rao_amplitude[peak_idx]

    return {
        'peak_frequency_rad_s': peak_omega,
        'peak_period_s': peak_period,
        'peak_rao': peak_rao,
        'resonance_detected': peak_rao > 2.0  # Typical threshold
    }

# Example
frequencies = np.linspace(0.1, 2.0, 100)
rao_amplitudes = 1.5 / np.sqrt((1 - (frequencies/0.5)**2)**2 + (0.1*frequencies/0.5)**2)

peak_info = find_rao_peak_period(frequencies, rao_amplitudes)
print(f"Natural period: {peak_info['peak_period_s']:.2f} s")
print(f"Peak RAO: {peak_info['peak_rao']:.2f} m/m")
```
