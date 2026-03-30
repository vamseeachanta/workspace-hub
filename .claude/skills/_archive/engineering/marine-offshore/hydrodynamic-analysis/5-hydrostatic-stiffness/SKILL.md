---
name: hydrodynamic-analysis-5-hydrostatic-stiffness
description: 'Sub-skill of hydrodynamic-analysis: 5. Hydrostatic Stiffness (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 5. Hydrostatic Stiffness (+1)

## 5. Hydrostatic Stiffness


**Stiffness Matrix:**
```python
def calculate_hydrostatic_stiffness(
    waterplane_area: float,
    center_of_buoyancy: np.ndarray,
    metacentric_height_long: float,
    metacentric_height_trans: float,
    displacement: float,
    rho: float = 1025
) -> np.ndarray:
    """
    Calculate 6x6 hydrostatic stiffness matrix.

    Args:
        waterplane_area: Waterplane area (m²)
        center_of_buoyancy: [x, y, z] position (m)
        metacentric_height_long: Longitudinal GM (m)
        metacentric_height_trans: Transverse GM (m)
        displacement: Vessel displacement (tonnes)
        rho: Water density (kg/m³)

    Returns:
        6x6 hydrostatic stiffness matrix
    """
    g = 9.81
    mass = displacement * 1000  # kg

    K = np.zeros((6, 6))

    # Heave stiffness: K_33 = ρ g A_wp
    K[2, 2] = rho * g * waterplane_area

    # Roll stiffness: K_44 = ρ g ∇ GM_T
    K[3, 3] = mass * g * metacentric_height_trans

    # Pitch stiffness: K_55 = ρ g ∇ GM_L
    K[4, 4] = mass * g * metacentric_height_long

    # Heave-pitch coupling
    K[2, 4] = -rho * g * waterplane_area * center_of_buoyancy[0]
    K[4, 2] = K[2, 4]

    # Heave-roll coupling
    K[2, 3] = -rho * g * waterplane_area * center_of_buoyancy[1]
    K[3, 2] = K[2, 3]

    return K

# Example: FPSO hydrostatic stiffness
K_hydro = calculate_hydrostatic_stiffness(
    waterplane_area=15000,  # m²
    center_of_buoyancy=np.array([160, 0, -10]),  # m
    metacentric_height_long=5.0,  # m
    metacentric_height_trans=3.0,  # m
    displacement=150000  # tonnes
)

print("Hydrostatic Stiffness Matrix:")
print(K_hydro)
```


## 6. Wave Spectra and Irregular Seas


**JONSWAP Spectrum:**
```python
def jonswap_spectrum(
    frequencies: np.ndarray,
    Hs: float,
    Tp: float,
    gamma: float = 3.3
) -> np.ndarray:
    """
    Calculate JONSWAP wave spectrum.

    S(f) = α g² (2π)^-4 f^-5 exp[-5/4(f/fp)^-4] γ^exp[-(f-fp)²/(2σ²fp²)]

    Args:
        frequencies: Frequency array (Hz)
        Hs: Significant wave height (m)
        Tp: Peak period (s)
        gamma: Peak enhancement factor (default 3.3)

    Returns:
        Spectral density S(f) (m²/Hz)
    """
    g = 9.81
    fp = 1 / Tp  # Peak frequency

    # Phillips constant
    alpha = 5.0 / 16.0 * Hs**2 * fp**4 / g**2

    # Spectral width parameter
    sigma = np.where(frequencies <= fp, 0.07, 0.09)

    # JONSWAP spectrum
    S_PM = alpha * g**2 * (2*np.pi)**(-4) * frequencies**(-5) * \
           np.exp(-5/4 * (frequencies / fp)**(-4))

    # Peak enhancement
    gamma_factor = gamma ** np.exp(-(frequencies - fp)**2 / (2 * sigma**2 * fp**2))

    S_JONSWAP = S_PM * gamma_factor

    return S_JONSWAP

# Example: Generate JONSWAP spectrum
freq = np.linspace(0.01, 0.5, 500)  # Hz
S = jonswap_spectrum(freq, Hs=8.5, Tp=12.0, gamma=3.3)

# Check Hs from spectrum
m0 = np.trapz(S, freq)  # Zero-order moment
Hs_calculated = 4 * np.sqrt(m0)

print(f"Input Hs: 8.5 m")
print(f"Calculated Hs from spectrum: {Hs_calculated:.2f} m")
```

**Response Spectrum:**
```python
def calculate_response_spectrum(
    wave_spectrum: np.ndarray,
    rao_amplitude: np.ndarray,
    frequencies: np.ndarray
) -> tuple[np.ndarray, dict]:
    """
    Calculate response spectrum from wave spectrum and RAO.

    S_response(ω) = |RAO(ω)|² * S_wave(ω)

    Args:
        wave_spectrum: Wave spectral density
        rao_amplitude: RAO amplitude (m/m)
        frequencies: Frequency array

    Returns:
        (response_spectrum, statistics)
    """
    # Response spectrum
    S_response = rao_amplitude**2 * wave_spectrum

    # Calculate statistics
    m0 = np.trapz(S_response, frequencies)  # Variance
    m2 = np.trapz(S_response * frequencies**2, frequencies)

    # Response statistics
    stats = {
        'variance': m0,
        'std_dev': np.sqrt(m0),
        'significant_amplitude': 2 * np.sqrt(m0),  # ≈ H_1/3 for motions
        'zero_crossing_period': 2 * np.pi * np.sqrt(m0 / m2)
    }

    return S_response, stats

# Example
freq = np.linspace(0.01, 0.5, 500)
S_wave = jonswap_spectrum(freq, Hs=8.5, Tp=12.0)

# Sample heave RAO
rao_heave = 1.2 / np.sqrt((1 - (2*np.pi*freq / 0.6)**2)**2 + (0.1 * 2*np.pi*freq / 0.6)**2)

S_heave, stats_heave = calculate_response_spectrum(S_wave, rao_heave, freq)

print(f"Significant heave amplitude: {stats_heave['significant_amplitude']:.2f} m")
print(f"Heave zero-crossing period: {stats_heave['zero_crossing_period']:.2f} s")
```
