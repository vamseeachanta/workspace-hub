---
name: wave-theory-example-1-complete-wave-analysis
description: 'Sub-skill of wave-theory: Example 1: Complete Wave Analysis.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Example 1: Complete Wave Analysis

## Example 1: Complete Wave Analysis


```python
def complete_wave_analysis(
    Hs: float,
    Tp: float,
    depth: float,
    duration: float = 3600,
    output_dir: str = 'reports/wave_analysis'
) -> dict:
    """
    Complete wave analysis: spectrum, time series, statistics.

    Args:
        Hs: Significant wave height (m)
        Tp: Peak period (s)
        depth: Water depth (m)
        duration: Time series duration (s)
        output_dir: Output directory

    Returns:
        Complete analysis results
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from pathlib import Path

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 1. Generate spectrum
    freq = np.linspace(0.01, 0.5, 500)
    S = jonswap_spectrum(freq, Hs, Tp)

    # 2. Calculate spectral parameters
    params = calculate_spectral_parameters(S, freq)

    # 3. Generate time series
    t, eta = generate_irregular_wave_time_series(S, freq, duration, dt=0.1)

    # 4. Wave statistics
    wave_stats = significant_wave_statistics(Hs)

    # 5. Regular wave properties (using Tp)
    regular_wave = airy_wave_properties(Hs, Tp, depth)

    # 6. Create visualizations
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'JONSWAP Spectrum',
            'Wave Elevation Time Series',
            'Wave Height Distribution',
            'Wave Steepness'
        )
    )

    # Plot 1: Spectrum
    fig.add_trace(
        go.Scatter(x=freq, y=S, name='S(f)', line=dict(color='blue')),
        row=1, col=1
    )

    # Plot 2: Time series (first 10 minutes)
    t_plot = t[:6000]
    eta_plot = eta[:6000]
    fig.add_trace(
        go.Scatter(x=t_plot, y=eta_plot, name='η(t)', line=dict(width=1)),
        row=1, col=2
    )

    # Plot 3: Wave height distribution
    H_array = np.linspace(0, Hs*2, 100)
    P_exceedance = rayleigh_distribution(H_array, Hs)

    fig.add_trace(
        go.Scatter(
            x=H_array, y=P_exceedance,
            name='Rayleigh',
            line=dict(color='red')
        ),
        row=2, col=1
    )

    # Plot 4: Steepness vs frequency
    steepness_freq = (2*np.pi*freq)**2 / 9.81 * np.sqrt(S)

    fig.add_trace(
        go.Scatter(x=freq, y=steepness_freq, name='Steepness'),
        row=2, col=2
    )

    fig.update_layout(height=800, showlegend=True, title_text=f'Wave Analysis (Hs={Hs}m, Tp={Tp}s)')
    fig.write_html(output_path / 'wave_analysis.html')

    # Export summary
    summary = {
        'input': {
            'Hs': Hs,
            'Tp': Tp,
            'depth': depth
        },
        'spectral_params': params,
        'statistics': wave_stats,
        'regular_wave': regular_wave,
        'time_series': {
            'duration_s': duration,
            'timestep_s': 0.1,
            'points': len(t)
        }
    }

    import json
    with open(output_path / 'wave_summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"✓ Wave analysis complete")
    print(f"  Output: {output_dir}")

    return summary

# Example
analysis = complete_wave_analysis(
    Hs=8.5,
    Tp=12.0,
    depth=1500,
    duration=3600
)
```
