---
name: numpy-numerical-analysis-4-fft-and-frequency-analysis
description: 'Sub-skill of numpy-numerical-analysis: 4. FFT and Frequency Analysis.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 4. FFT and Frequency Analysis

## 4. FFT and Frequency Analysis


**FFT for Spectral Analysis:**
```python
def compute_fft_spectrum(
    time_series: np.ndarray,
    dt: float,
    window: str = 'hann'
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute FFT spectrum of time series.

    Args:
        time_series: Time series data
        dt: Time step
        window: Window function ('hann', 'hamming', 'blackman')

    Returns:
        (frequencies, amplitude_spectrum)
    """
    n = len(time_series)

    # Apply window
    if window == 'hann':
        windowed = time_series * np.hanning(n)
    elif window == 'hamming':
        windowed = time_series * np.hamming(n)
    elif window == 'blackman':
        windowed = time_series * np.blackman(n)
    else:
        windowed = time_series

    # Compute FFT
    fft_result = np.fft.fft(windowed)

    # Compute frequencies
    frequencies = np.fft.fftfreq(n, d=dt)

    # Amplitude spectrum (single-sided)
    amplitude = np.abs(fft_result)[:n//2] * 2 / n
    frequencies_positive = frequencies[:n//2]

    return frequencies_positive, amplitude

# Example: Analyze wave elevation time series
import numpy as np

# Generate sample wave elevation (3 components)
t = np.linspace(0, 100, 10000)  # 100 seconds, 10000 points
dt = t[1] - t[0]

# Wave components: 6s, 8s, 10s periods
wave = (
    2.0 * np.sin(2*np.pi*t / 6) +
    1.5 * np.sin(2*np.pi*t / 8) +
    1.0 * np.sin(2*np.pi*t / 10)
)

# Add noise
wave += 0.2 * np.random.randn(len(t))

# Compute spectrum
freq, amplitude = compute_fft_spectrum(wave, dt, window='hann')

# Find peaks
peak_indices = np.argsort(amplitude)[-3:]  # Top 3 peaks
peak_frequencies = freq[peak_indices]
peak_periods = 1 / peak_frequencies

print("Detected wave periods:")
for period in sorted(peak_periods, reverse=True):
    print(f"  T = {period:.2f} s")
```

**Power Spectral Density:**
```python
def compute_power_spectral_density(
    time_series: np.ndarray,
    dt: float,
    nfft: int = None
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute power spectral density using Welch's method.

    Args:
        time_series: Time series data
        dt: Time step
        nfft: FFT length (None = length of time series)

    Returns:
        (frequencies, PSD)
    """
    from scipy import signal

    # Compute PSD using Welch's method
    frequencies, psd = signal.welch(
        time_series,
        fs=1/dt,
        nperseg=nfft or len(time_series)//8,
        window='hann'
    )

    return frequencies, psd

# Example: Wave spectral analysis
t = np.linspace(0, 3600, 36000)  # 1 hour, 10 Hz sampling
dt = t[1] - t[0]

# JONSWAP spectrum simulation (simplified)
wave_elevation = np.random.randn(len(t)) * 2.0  # Simplified

freq, psd = compute_power_spectral_density(wave_elevation, dt)

# Calculate Hs from PSD
m0 = np.trapz(psd, freq)  # Zero-order moment
Hs = 4 * np.sqrt(m0)

print(f"Significant wave height: {Hs:.2f} m")
```
