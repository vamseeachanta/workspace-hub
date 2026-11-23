---
name: ship-dynamics-6dof-example-1-full-6dof-simulation
description: 'Sub-skill of ship-dynamics-6dof: Example 1: Full 6DOF Simulation.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Example 1: Full 6DOF Simulation

## Example 1: Full 6DOF Simulation


```python
def simulate_vessel_6dof_in_waves(
    vessel_properties: dict,
    wave_conditions: dict,
    duration: float = 3600,
    dt: float = 0.1
) -> dict:
    """
    Complete 6DOF vessel simulation in irregular waves.

    Args:
        vessel_properties: Vessel mass, stiffness, damping
        wave_conditions: Hs, Tp, heading
        duration: Simulation duration (s)
        dt: Time step (s)

    Returns:
        Complete motion results
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Time array
    t = np.arange(0, duration, dt)
    n_steps = len(t)

    # Extract properties
    M = vessel_properties['mass_matrix']
    C_damp = vessel_properties['damping_matrix']
    K = vessel_properties['stiffness_matrix']

    # Generate wave forces (simplified JONSWAP spectrum)
    Hs = wave_conditions['Hs']
    Tp = wave_conditions['Tp']
    heading = wave_conditions['heading']  # degrees

    # Wave force time series (simplified)
    omega_p = 2 * np.pi / Tp
    F_wave = np.zeros((n_steps, 6))

    # Generate forces for each DOF based on heading
    if heading == 0:  # Head seas
        F_wave[:, 0] = Hs * 1e5 * np.sin(omega_p * t)  # Surge
        F_wave[:, 2] = Hs * 5e5 * np.sin(omega_p * t)  # Heave
        F_wave[:, 4] = Hs * 1e6 * np.sin(omega_p * t)  # Pitch
    elif heading == 90:  # Beam seas
        F_wave[:, 1] = Hs * 1e5 * np.sin(omega_p * t)  # Sway
        F_wave[:, 3] = Hs * 2e6 * np.sin(omega_p * t)  # Roll

    # Add random component for irregular seas
    for i in range(6):
        F_wave[:, i] += np.random.randn(n_steps) * 0.2 * np.std(F_wave[:, i])

    # Run simulation
    result = newmark_beta_integration(
        M, C_damp, K, F_wave,
        x0=np.zeros(6), v0=np.zeros(6), t=t
    )

    # Calculate statistics for all DOFs
    dof_names = ['Surge', 'Sway', 'Heave', 'Roll', 'Pitch', 'Yaw']
    statistics = {}

    for i, dof in enumerate(dof_names):
        statistics[dof] = calculate_seakeeping_statistics(
            result['displacement'][:, i], dt, dof
        )

    # Create visualization
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=dof_names
    )

    for i, dof in enumerate(dof_names):
        row = i // 3 + 1
        col = i % 3 + 1

        fig.add_trace(
            go.Scatter(
                x=t,
                y=result['displacement'][:, i],
                name=dof,
                showlegend=False
            ),
            row=row, col=col
        )

    fig.update_layout(
        title=f'6DOF Vessel Motions (Hs={Hs}m, Tp={Tp}s, Heading={heading}°)',
        height=800
    )

    fig.write_html('reports/6dof_simulation.html')

    return {
        'time': t,
        'motions': result,
        'statistics': statistics,
        'wave_conditions': wave_conditions
    }

# Example usage
vessel = {
    'mass_matrix': M_fpso,
    'damping_matrix': np.diag([50e6, 50e6, 100e6, 5e8, 5e8, 2e8]),
    'stiffness_matrix': C_hydro
}

waves = {
    'Hs': 8.5,
    'Tp': 12.0,
    'heading': 0  # Head seas
}

results = simulate_vessel_6dof_in_waves(vessel, waves, duration=600, dt=0.1)

print("Motion Statistics:")
for dof, stats in results['statistics'].items():
    print(f"{dof}: Sig = {stats['significant_amplitude']:.2f}, Max = {stats['max_amplitude']:.2f}")
```
