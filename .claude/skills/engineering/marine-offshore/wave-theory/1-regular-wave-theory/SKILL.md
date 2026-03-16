---
name: wave-theory-1-regular-wave-theory
description: 'Sub-skill of wave-theory: 1. Regular Wave Theory.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 1. Regular Wave Theory

## 1. Regular Wave Theory


**Linear (Airy) Wave Theory:**
```python
import numpy as np

def airy_wave_properties(
    H: float,
    T: float,
    d: float,
    g: float = 9.81
) -> dict:
    """
    Calculate Airy wave properties.

    Valid for: H/L < 0.14, d/L > 0.5 (deep water) or d/L < 0.05 (shallow)

    Args:
        H: Wave height (m)
        T: Wave period (s)
        d: Water depth (m)
        g: Gravity (m/s²)

    Returns:
        Wave properties dictionary
    """
    # Wave frequency
    omega = 2 * np.pi / T

    # Dispersion relation: ω² = gk·tanh(kd)
    # Solve iteratively for wave number k
    from scipy.optimize import fsolve

    def dispersion(k):
        return omega**2 - g * k * np.tanh(k * d)

    k0 = omega**2 / g  # Deep water approximation
    k = fsolve(dispersion, k0)[0]

    # Wave length
    L = 2 * np.pi / k

    # Wave celerity (phase speed)
    C = omega / k

    # Group velocity
    n = 0.5 * (1 + 2*k*d / np.sinh(2*k*d))  # Shoaling coefficient
    Cg = n * C

    # Deep water classification
    if d / L > 0.5:
        regime = "Deep water"
    elif d / L < 0.05:
        regime = "Shallow water"
    else:
        regime = "Intermediate"

    return {
        'height_m': H,
        'period_s': T,
        'depth_m': d,
        'wavelength_m': L,
        'wave_number': k,
        'frequency_rad_s': omega,
        'frequency_hz': omega / (2*np.pi),
        'celerity_m_s': C,
        'group_velocity_m_s': Cg,
        'regime': regime,
        'd_over_L': d / L,
        'H_over_L': H / L,
        'steepness': H / L
    }

# Example
wave = airy_wave_properties(H=8, T=12, d=1500)

print(f"Wave Properties (H={wave['height_m']}m, T={wave['period_s']}s):")
print(f"  Wavelength: {wave['wavelength_m']:.1f} m")
print(f"  Regime: {wave['regime']} (d/L = {wave['d_over_L']:.3f})")
print(f"  Celerity: {wave['celerity_m_s']:.2f} m/s")
print(f"  Steepness: {wave['steepness']:.4f}")
```

**Wave Kinematics:**
```python
def wave_particle_kinematics(
    z: float,
    H: float,
    T: float,
    d: float,
    t: float = 0,
    x: float = 0,
    g: float = 9.81
) -> dict:
    """
    Calculate wave particle velocities and accelerations.

    Args:
        z: Vertical position (0 at SWL, negative below)
        H: Wave height (m)
        T: Wave period (s)
        d: Water depth (m)
        t: Time (s)
        x: Horizontal position (m)
        g: Gravity (m/s²)

    Returns:
        Particle kinematics
    """
    # Wave properties
    wave = airy_wave_properties(H, T, d, g)
    k = wave['wave_number']
    omega = wave['frequency_rad_s']

    # Amplitude
    a = H / 2

    # Hyperbolic functions
    cosh_kz_d = np.cosh(k * (z + d))
    sinh_kz_d = np.sinh(k * (z + d))
    cosh_kd = np.cosh(k * d)
    sinh_kd = np.sinh(k * d)

    # Wave phase
    phase = k * x - omega * t

    # Horizontal velocity
    u = (omega * a * cosh_kz_d / sinh_kd) * np.cos(phase)

    # Vertical velocity
    w = (omega * a * sinh_kz_d / sinh_kd) * np.sin(phase)

    # Horizontal acceleration
    ax = -(omega**2 * a * cosh_kz_d / sinh_kd) * np.sin(phase)

    # Vertical acceleration
    az = (omega**2 * a * sinh_kz_d / sinh_kd) * np.cos(phase)

    # Dynamic pressure
    p_dynamic = g * a * (cosh_kz_d / cosh_kd) * np.cos(phase)

    return {
        'horizontal_velocity': u,
        'vertical_velocity': w,
        'horizontal_acceleration': ax,
        'vertical_acceleration': az,
        'dynamic_pressure': p_dynamic,
        'total_velocity': np.sqrt(u**2 + w**2),
        'total_acceleration': np.sqrt(ax**2 + az**2)
    }

# Example: Surface velocity (z=0)
kinematics = wave_particle_kinematics(z=0, H=8, T=12, d=1500, t=0, x=0)

print(f"Surface Particle Kinematics:")
print(f"  Horizontal velocity: {kinematics['horizontal_velocity']:.2f} m/s")
print(f"  Vertical velocity: {kinematics['vertical_velocity']:.2f} m/s")
print(f"  Total velocity: {kinematics['total_velocity']:.2f} m/s")
```
