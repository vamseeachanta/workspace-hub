---
name: hydrodynamic-analysis-application-1-complete-rao-analysis
description: 'Sub-skill of hydrodynamic-analysis: Application 1: Complete RAO Analysis
  (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Application 1: Complete RAO Analysis (+1)

## Application 1: Complete RAO Analysis


```python
def complete_rao_analysis(
    bem_results_file: str,
    wave_headings: np.ndarray = None,
    output_dir: str = 'reports/rao_analysis'
) -> dict:
    """
    Complete RAO analysis from BEM results.

    Args:
        bem_results_file: Path to BEM results (WAMIT .out or AQWA .lis)
        wave_headings: Wave heading array (degrees)
        output_dir: Output directory

    Returns:
        RAO results dictionary
    """
    import pandas as pd
    from pathlib import Path

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if wave_headings is None:
        wave_headings = np.arange(0, 360, 30)

    # Load BEM results (example format)
    # In reality, parse WAMIT .out or AQWA results
    frequencies = np.linspace(0.1, 2.0, 50)  # rad/s
    periods = 2 * np.pi / frequencies

    # Sample RAO data (6 DOFs x n_frequencies x n_headings)
    raos = {}
    dof_names = ['Surge', 'Sway', 'Heave', 'Roll', 'Pitch', 'Yaw']

    for heading in wave_headings:
        for i, dof in enumerate(dof_names):
            # Simplified RAO calculation
            # In practice, read from BEM output
            if heading == 0:  # Head seas
                if dof == 'Surge':
                    rao = 0.8 * np.ones_like(frequencies)
                elif dof == 'Heave':
                    rao = 1.2 / np.sqrt((1 - (frequencies/0.6)**2)**2 + (0.1*frequencies/0.6)**2)
                elif dof == 'Pitch':
                    rao = 0.05 * frequencies / (1 + (frequencies/0.6)**2)
                else:
                    rao = np.zeros_like(frequencies)
            else:
                # Simplified for other headings
                rao = np.random.rand(len(frequencies)) * 0.5

            raos[(heading, dof)] = rao

    # Export RAOs to CSV
    for dof in dof_names:
        df_rao = pd.DataFrame({
            'Period_s': periods,
            **{f'Heading_{h}deg': raos[(h, dof)] for h in wave_headings}
        })

        df_rao.to_csv(output_path / f'RAO_{dof}.csv', index=False)

    # Create polar plot
    import plotly.graph_objects as go

    fig = go.Figure()

    for dof in ['Surge', 'Heave', 'Pitch']:
        rao_at_peak = [raos[(h, dof)][25] for h in wave_headings]  # At T=10s

        fig.add_trace(go.Scatterpolar(
            r=rao_at_peak,
            theta=wave_headings,
            name=dof,
            mode='lines+markers'
        ))

    fig.update_layout(
        title='RAO Polar Plot (T = 10s)',
        polar=dict(radialaxis=dict(visible=True))
    )

    fig.write_html(output_path / 'RAO_polar.html')

    print(f"✓ RAO analysis complete")
    print(f"  Output: {output_dir}")

    return raos

# Usage
rao_results = complete_rao_analysis(
    bem_results_file='data/processed/wamit_results.out',
    wave_headings=np.array([0, 45, 90, 135, 180])
)
```


## Application 2: Motion Prediction in Irregular Seas


```python
def predict_vessel_motions_irregular_seas(
    Hs: float,
    Tp: float,
    heading: float,
    rao_data: dict,
    duration: float = 3600
) -> dict:
    """
    Predict vessel motions in irregular seas.

    Args:
        Hs: Significant wave height (m)
        Tp: Peak period (s)
        heading: Wave heading (degrees)
        rao_data: RAO dictionary from BEM analysis
        duration: Simulation duration (s)

    Returns:
        Motion statistics
    """
    # Frequency array
    freq_hz = np.linspace(0.01, 0.5, 500)
    omega = 2 * np.pi * freq_hz

    # Wave spectrum
    S_wave = jonswap_spectrum(freq_hz, Hs, Tp)

    # Calculate response spectra
    dof_names = ['Surge', 'Sway', 'Heave', 'Roll', 'Pitch', 'Yaw']
    motion_stats = {}

    for dof in dof_names:
        # Get RAO for this heading and DOF
        # Simplified: use constant RAO
        rao_amplitude = np.interp(
            omega,
            np.linspace(0.1, 2.0, 50),
            rao_data.get((heading, dof), np.zeros(50))
        )

        # Response spectrum
        S_response, stats = calculate_response_spectrum(S_wave, rao_amplitude, freq_hz)

        motion_stats[dof] = {
            'std_dev': stats['std_dev'],
            'significant_amplitude': stats['significant_amplitude'],
            'max_expected': stats['significant_amplitude'] * 1.86  # Rayleigh distribution
        }

    return motion_stats

# Example
motion_predictions = predict_vessel_motions_irregular_seas(
    Hs=8.5,
    Tp=12.0,
    heading=0,  # Head seas
    rao_data=rao_results,
    duration=10800  # 3 hours
)

print("Predicted Motion Statistics:")
for dof, stats in motion_predictions.items():
    print(f"{dof}:")
    print(f"  Significant amplitude: {stats['significant_amplitude']:.2f}")
    print(f"  Max expected (3hr): {stats['max_expected']:.2f}")
```
