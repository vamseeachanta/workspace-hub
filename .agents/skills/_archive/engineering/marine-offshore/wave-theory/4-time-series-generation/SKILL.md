---
name: wave-theory-4-time-series-generation
description: 'Sub-skill of wave-theory: 4. Time Series Generation (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 4. Time Series Generation (+1)

## 4. Time Series Generation


**Generate Irregular Wave Time Series:**
```python
def generate_irregular_wave_time_series(
    S: np.ndarray,
    frequencies: np.ndarray,
    duration: float,
    dt: float,
    random_seed: int = None
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate irregular wave elevation time series from spectrum.

    Args:
        S: Wave spectrum (m²/Hz)
        frequencies: Frequency array (Hz)
        duration: Duration (s)
        dt: Time step (s)
        random_seed: Random seed for reproducibility

    Returns:
        (time, elevation) arrays
    """
    if random_seed is not None:
        np.random.seed(random_seed)

    # Time array
    time = np.arange(0, duration, dt)

    # Initialize elevation
    eta = np.zeros_like(time)

    # Frequency resolution
    df = frequencies[1] - frequencies[0]

    # Generate wave components
    for i, f in enumerate(frequencies):
        if S[i] > 0:
            # Amplitude from spectrum
            amplitude = np.sqrt(2 * S[i] * df)

            # Random phase
            phase = np.random.uniform(0, 2*np.pi)

            # Wave component
            omega = 2 * np.pi * f
            eta += amplitude * np.cos(omega * time + phase)

    return time, eta

# Example: Generate 1 hour of wave data
t, elevation = generate_irregular_wave_time_series(
    S, freq,
    duration=3600,
    dt=0.1,
    random_seed=42
)

# Verify statistics
Hs_timeseries = 4 * np.std(elevation)

print(f"Time Series Statistics:")
print(f"  Target Hs: {params['Hs']:.2f} m")
print(f"  Generated Hs: {Hs_timeseries:.2f} m")
print(f"  Duration: {len(t) * 0.1 / 3600:.2f} hours")
```


## 5. Wave Scatter Diagrams


**Create Wave Scatter Diagram:**
```python
def create_wave_scatter_diagram(
    Hs_bins: np.ndarray,
    Tp_bins: np.ndarray,
    location_data: dict
) -> np.ndarray:
    """
    Create wave scatter diagram (probability table).

    Args:
        Hs_bins: Hs bin edges (m)
        Tp_bins: Tp bin edges (s)
        location_data: Historical wave data or hindcast

    Returns:
        Probability matrix (sum = 1.0)
    """
    # This is typically based on hindcast data
    # Simplified example using lognormal distribution

    n_Hs = len(Hs_bins) - 1
    n_Tp = len(Tp_bins) - 1

    scatter = np.zeros((n_Hs, n_Tp))

    # Simplified: Tp roughly proportional to sqrt(Hs)
    for i in range(n_Hs):
        Hs_mid = (Hs_bins[i] + Hs_bins[i+1]) / 2

        # Expected Tp for this Hs (empirical: Tp ≈ 3.6*sqrt(Hs))
        Tp_expected = 3.6 * np.sqrt(Hs_mid)

        # Hs occurrence (Weibull distribution)
        from scipy.stats import weibull_min
        p_Hs = weibull_min.pdf(Hs_mid, c=2, scale=2.5)

        # Tp distribution given Hs (normal around expected)
        from scipy.stats import norm
        for j in range(n_Tp):
            Tp_mid = (Tp_bins[j] + Tp_bins[j+1]) / 2
            p_Tp_given_Hs = norm.pdf(Tp_mid, loc=Tp_expected, scale=1.5)

            scatter[i, j] = p_Hs * p_Tp_given_Hs

    # Normalize to probabilities
    scatter /= scatter.sum()

    return scatter

# Example
Hs_bins = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
Tp_bins = np.array([0, 4, 6, 8, 10, 12, 14, 16])

scatter = create_wave_scatter_diagram(Hs_bins, Tp_bins, {})

# Annual hours
annual_hours = scatter * 8760

print(f"Wave Scatter Diagram:")
print(f"  Total probability: {scatter.sum():.4f}")
print(f"  Most probable sea state: Hs={Hs_bins[np.unravel_index(scatter.argmax(), scatter.shape)[0]]}-{Hs_bins[np.unravel_index(scatter.argmax(), scatter.shape)[0]+1]}m")
```
