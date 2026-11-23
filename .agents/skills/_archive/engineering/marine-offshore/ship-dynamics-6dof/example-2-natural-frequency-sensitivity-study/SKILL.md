---
name: ship-dynamics-6dof-example-2-natural-frequency-sensitivity-study
description: 'Sub-skill of ship-dynamics-6dof: Example 2: Natural Frequency Sensitivity
  Study.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Example 2: Natural Frequency Sensitivity Study

## Example 2: Natural Frequency Sensitivity Study


```python
def natural_frequency_sensitivity_study(
    base_properties: dict,
    parameter_ranges: dict
) -> dict:
    """
    Sensitivity study of natural frequencies to design parameters.

    Args:
        base_properties: Base vessel properties
        parameter_ranges: Parameters to vary

    Returns:
        Sensitivity results
    """
    import plotly.graph_objects as go

    results = {}

    for param_name, param_values in parameter_ranges.items():
        natural_periods = []

        for value in param_values:
            # Update property
            props = base_properties.copy()

            if param_name == 'GMT':
                # Update roll stiffness
                props['K'][3, 3] *= value / base_properties['GMT']
            elif param_name == 'Rxx':
                # Update roll inertia
                m = props['M'][0, 0]
                props['M'][3, 3] = m * value**2

            # Calculate natural frequencies
            freq_result = calculate_coupled_natural_frequencies(
                props['M'], props['K']
            )

            natural_periods.append(freq_result['periods_s'][3])  # Roll period

        results[param_name] = {
            'values': param_values,
            'roll_periods': natural_periods
        }

    # Plot sensitivity
    fig = go.Figure()

    for param_name, data in results.items():
        fig.add_trace(go.Scatter(
            x=data['values'],
            y=data['roll_periods'],
            name=param_name,
            mode='lines+markers'
        ))

    fig.update_layout(
        title='Roll Natural Period Sensitivity',
        xaxis_title='Parameter Value',
        yaxis_title='Roll Natural Period (s)'
    )

    fig.write_html('reports/sensitivity_analysis.html')

    return results

# Example
base = {
    'M': M_fpso,
    'K': C_hydro,
    'GMT': 3.0
}

param_ranges = {
    'GMT': np.linspace(1.0, 5.0, 20),  # m
    'Rxx': np.linspace(18, 26, 20)     # m
}

sensitivity = natural_frequency_sensitivity_study(base, param_ranges)
```
