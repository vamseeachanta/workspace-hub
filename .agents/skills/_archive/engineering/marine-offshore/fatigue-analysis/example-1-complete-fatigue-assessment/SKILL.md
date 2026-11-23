---
name: fatigue-analysis-example-1-complete-fatigue-assessment
description: 'Sub-skill of fatigue-analysis: Example 1: Complete Fatigue Assessment.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Example 1: Complete Fatigue Assessment

## Example 1: Complete Fatigue Assessment


```python
def complete_fatigue_assessment(
    tension_file: str,
    output_dir: str = 'reports/fatigue'
) -> dict:
    """
    Complete fatigue assessment from tension time series.

    Args:
        tension_file: CSV file with tension time series
        output_dir: Output directory

    Returns:
        Fatigue assessment results
    """
    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from pathlib import Path

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load tension data
    df = pd.read_csv(tension_file)
    tension = df['Tension'].values  # kN
    time = df['Time'].values  # seconds

    # Rainflow counting
    ranges, counts = rainflow_counting(tension)

    # Chain properties
    chain_diameter = 127  # mm
    sn_curve = get_dnv_sn_curve('F3', thickness=chain_diameter)

    # Calculate fatigue
    fatigue = mooring_chain_fatigue_analysis(
        tension,
        chain_diameter=chain_diameter,
        design_life_years=25,
        time_step=time[1] - time[0]
    )

    # Create visualizations
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Tension Time Series',
            'Rainflow Histogram',
            'S-N Curve with Load Points',
            'Damage Breakdown'
        )
    )

    # Plot 1: Time series
    fig.add_trace(
        go.Scatter(x=time, y=tension, name='Tension', line=dict(width=1)),
        row=1, col=1
    )

    # Plot 2: Rainflow histogram
    fig.add_trace(
        go.Bar(x=ranges, y=counts, name='Cycle Counts'),
        row=1, col=2
    )

    # Plot 3: S-N curve
    stress_plot = np.logspace(0, 3, 100)
    N_plot = sn_curve['a1'] / stress_plot**sn_curve['m1']

    fig.add_trace(
        go.Scatter(
            x=N_plot, y=stress_plot,
            mode='lines', name='S-N Curve F3',
            line=dict(color='red')
        ),
        row=2, col=1
    )

    # Add load points
    stress_ranges_chain = fatigue['stress_ranges']
    N_values = [calculate_cycles_to_failure(s, sn_curve) for s in stress_ranges_chain]

    fig.add_trace(
        go.Scatter(
            x=N_values, y=stress_ranges_chain,
            mode='markers', name='Load Points',
            marker=dict(size=8)
        ),
        row=2, col=1
    )

    fig.update_xaxes(type='log', title_text='Cycles N', row=2, col=1)
    fig.update_yaxes(type='log', title_text='Stress Range (MPa)', row=2, col=1)

    # Plot 4: Damage breakdown (top contributors)
    breakdown = fatigue_result['breakdown'][:10]  # Top 10
    damage_pct = [item['damage_percent'] for item in breakdown]
    stress_labels = [f"{item['stress_range']:.1f} MPa" for item in breakdown]

    fig.add_trace(
        go.Bar(x=stress_labels, y=damage_pct, name='Damage %'),
        row=2, col=2
    )

    fig.update_layout(height=800, showlegend=True, title_text='Fatigue Assessment Report')
    fig.write_html(output_path / 'fatigue_assessment.html')

    # Export summary
    summary = pd.DataFrame({
        'Parameter': [
            'Chain Diameter (mm)',
            'Chain Grade',
            'MBL (tonnes)',
            'Design Life (years)',
            'Total Damage',
            'Utilization (%)',
            'Fatigue Life (years)',
            'Status'
        ],
        'Value': [
            fatigue['chain_diameter_mm'],
            fatigue['chain_grade'],
            f"{fatigue['MBL_tonnes']:.1f}",
            fatigue['design_life_years'],
            f"{fatigue['fatigue_damage']:.4f}",
            f"{fatigue['utilization']*100:.1f}",
            f"{fatigue['fatigue_life_years']:.1f}",
            'PASS' if fatigue['passed'] else 'FAIL'
        ]
    })

    summary.to_csv(output_path / 'fatigue_summary.csv', index=False)

    print(f"✓ Fatigue assessment complete")
    print(f"  Output: {output_dir}")
    print(f"  Status: {'PASS' if fatigue['passed'] else 'FAIL'}")

    return fatigue
```
