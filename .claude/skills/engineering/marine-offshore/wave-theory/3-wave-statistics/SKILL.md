---
name: wave-theory-3-wave-statistics
description: 'Sub-skill of wave-theory: 3. Wave Statistics.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 3. Wave Statistics

## 3. Wave Statistics


**Spectral Parameters:**
```python
def calculate_spectral_parameters(
    S: np.ndarray,
    frequencies: np.ndarray
) -> dict:
    """
    Calculate spectral wave parameters.

    Args:
        S: Wave spectrum (m²/Hz)
        frequencies: Frequency array (Hz)

    Returns:
        Spectral parameters
    """
    # Spectral moments
    m0 = np.trapz(S, frequencies)
    m1 = np.trapz(S * frequencies, frequencies)
    m2 = np.trapz(S * frequencies**2, frequencies)
    m4 = np.trapz(S * frequencies**4, frequencies)

    # Significant wave height
    Hs = 4 * np.sqrt(m0)

    # Mean period
    Tm01 = m0 / m1

    # Zero-crossing period
    Tz = np.sqrt(m0 / m2)

    # Peak period (from spectrum maximum)
    peak_idx = np.argmax(S)
    Tp = 1 / frequencies[peak_idx]

    # Spectral width
    epsilon = np.sqrt(1 - m2**2 / (m0 * m4))

    # Wave steepness
    k_mean = 2 * np.pi / (9.81 * Tz**2 / (2*np.pi))  # Deep water approx
    steepness = k_mean * Hs / 2

    return {
        'm0': m0,
        'm1': m1,
        'm2': m2,
        'm4': m4,
        'Hs': Hs,
        'Tp': Tp,
        'Tz': Tz,
        'Tm01': Tm01,
        'spectral_width': epsilon,
        'steepness': steepness
    }

# Example
params = calculate_spectral_parameters(S, freq)

print(f"Spectral Parameters:")
print(f"  Hs: {params['Hs']:.2f} m")
print(f"  Tp: {params['Tp']:.2f} s")
print(f"  Tz: {params['Tz']:.2f} s")
print(f"  Spectral width: {params['spectral_width']:.3f}")
```

**Wave Height Distribution:**
```python
def rayleigh_distribution(
    H: np.ndarray,
    Hs: float
) -> np.ndarray:
    """
    Rayleigh distribution for wave heights in irregular seas.

    P(H) = probability that wave height exceeds H

    Args:
        H: Wave height array (m)
        Hs: Significant wave height (m)

    Returns:
        Exceedance probability
    """
    # Rayleigh parameter
    H_rms = Hs / np.sqrt(2)

    # Exceedance probability
    P = np.exp(-(H / H_rms)**2)

    return P

def significant_wave_statistics(Hs: float) -> dict:
    """
    Calculate wave statistics from Hs using Rayleigh distribution.

    Args:
        Hs: Significant wave height (m)

    Returns:
        Wave statistics
    """
    H_rms = Hs / np.sqrt(2)

    # Various statistical wave heights
    H_mean = H_rms * np.sqrt(np.pi / 2)
    H_1_10 = H_rms * np.sqrt(2 * np.log(10))  # Average of highest 1/10
    H_1_100 = H_rms * np.sqrt(2 * np.log(100))  # Average of highest 1/100
    H_max_1000 = H_rms * np.sqrt(2 * np.log(1000))  # Most probable max in 1000 waves

    return {
        'Hs': Hs,
        'H_mean': H_mean,
        'H_rms': H_rms,
        'H_1_10': H_1_10,
        'H_1_100': H_1_100,
        'H_max_1000': H_max_1000
    }

# Example
stats = significant_wave_statistics(Hs=8.5)

print(f"Wave Statistics (Hs = {stats['Hs']} m):")
print(f"  Mean height: {stats['H_mean']:.2f} m")
print(f"  H_1/10: {stats['H_1_10']:.2f} m")
print(f"  H_1/100: {stats['H_1_100']:.2f} m")
print(f"  H_max (in 1000 waves): {stats['H_max_1000']:.2f} m")
```
