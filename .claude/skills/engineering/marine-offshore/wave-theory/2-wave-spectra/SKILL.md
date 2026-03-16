---
name: wave-theory-2-wave-spectra
description: 'Sub-skill of wave-theory: 2. Wave Spectra.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 2. Wave Spectra

## 2. Wave Spectra


**JONSWAP Spectrum:**
```python
def jonswap_spectrum(
    frequencies: np.ndarray,
    Hs: float,
    Tp: float,
    gamma: float = 3.3,
    alpha: float = None
) -> np.ndarray:
    """
    Calculate JONSWAP wave spectrum.

    S(f) = α g² (2π)^-4 f^-5 exp[-5/4(f/fp)^-4] γ^exp[-(f-fp)²/(2σ²fp²)]

    Args:
        frequencies: Frequency array (Hz)
        Hs: Significant wave height (m)
        Tp: Peak period (s)
        gamma: Peak enhancement factor (3.3 for North Sea)
        alpha: Phillips constant (calculated if None)

    Returns:
        Spectral density S(f) (m²/Hz)
    """
    g = 9.81
    fp = 1 / Tp  # Peak frequency (Hz)

    # Calculate alpha if not provided
    if alpha is None:
        # Relationship: Hs = 4*sqrt(m0)
        # For JONSWAP: alpha ≈ 5.061 * Hs² / Tp⁴ * (1 - 0.287*ln(γ))
        alpha = 5.061 * Hs**2 / Tp**4 * (1 - 0.287 * np.log(gamma))

    # Sigma parameter
    sigma = np.where(frequencies <= fp, 0.07, 0.09)

    # Pierson-Moskowitz spectrum
    S_PM = alpha * g**2 * (2*np.pi)**(-4) * frequencies**(-5) * \
           np.exp(-1.25 * (frequencies / fp)**(-4))

    # Peak enhancement
    r = np.exp(-(frequencies - fp)**2 / (2 * sigma**2 * fp**2))
    gamma_factor = gamma ** r

    # JONSWAP spectrum
    S = S_PM * gamma_factor

    return S

# Example: Generate JONSWAP spectrum
freq = np.linspace(0.01, 0.5, 500)
S = jonswap_spectrum(freq, Hs=8.5, Tp=12.0, gamma=3.3)

# Verify Hs
m0 = np.trapz(S, freq)
Hs_calc = 4 * np.sqrt(m0)

print(f"JONSWAP Spectrum:")
print(f"  Input Hs: 8.5 m")
print(f"  Calculated Hs: {Hs_calc:.2f} m")
print(f"  Peak frequency: {1/12:.4f} Hz")
```

**Pierson-Moskowitz Spectrum:**
```python
def pierson_moskowitz_spectrum(
    frequencies: np.ndarray,
    Hs: float,
    Tp: float = None,
    U19_5: float = None
) -> np.ndarray:
    """
    Calculate Pierson-Moskowitz spectrum (fully developed sea).

    Args:
        frequencies: Frequency array (Hz)
        Hs: Significant wave height (m)
        Tp: Peak period (s) - optional
        U19_5: Wind speed at 19.5m height (m/s) - optional

    Returns:
        Spectral density S(f) (m²/Hz)
    """
    g = 9.81

    if Tp is not None:
        # Use peak period
        fp = 1 / Tp
    elif U19_5 is not None:
        # Calculate from wind speed
        fp = 0.877 * g / (2 * np.pi * U19_5)
    else:
        raise ValueError("Must provide either Tp or U19_5")

    # Phillips constant
    alpha = 0.0081  # For fully developed seas

    # P-M spectrum
    S = alpha * g**2 * (2*np.pi)**(-4) * frequencies**(-5) * \
        np.exp(-1.25 * (frequencies / fp)**(-4))

    return S

# Example
S_PM = pierson_moskowitz_spectrum(freq, Hs=8.5, Tp=12.0)

m0_PM = np.trapz(S_PM, freq)
Hs_PM = 4 * np.sqrt(m0_PM)

print(f"P-M Spectrum Hs: {Hs_PM:.2f} m")
```
