---
name: hydrodynamic-analysis-application-3-added-mass-convergence-check
description: 'Sub-skill of hydrodynamic-analysis: Application 3: Added Mass Convergence
  Check.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Application 3: Added Mass Convergence Check

## Application 3: Added Mass Convergence Check


```python
def check_added_mass_convergence(
    panel_counts: list,
    added_mass_results: list
) -> dict:
    """
    Check convergence of added mass with panel count.

    Args:
        panel_counts: List of panel counts
        added_mass_results: List of 6x6 added mass matrices

    Returns:
        Convergence assessment
    """
    import plotly.graph_objects as go

    # Check heave added mass convergence
    A33_values = [A[2, 2] for A in added_mass_results]

    # Calculate relative change
    relative_changes = [
        abs(A33_values[i] - A33_values[i-1]) / A33_values[i-1] * 100
        for i in range(1, len(A33_values))
    ]

    # Plot convergence
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=panel_counts,
        y=A33_values,
        name='A33 (Heave Added Mass)',
        mode='lines+markers'
    ))

    fig.update_layout(
        title='Added Mass Convergence Study',
        xaxis_title='Panel Count',
        yaxis_title='A33 (tonnes)',
        hovermode='x unified'
    ))

    fig.write_html('reports/added_mass_convergence.html')

    # Convergence criteria: < 1% change
    converged = relative_changes[-1] < 1.0 if relative_changes else False

    return {
        'converged': converged,
        'final_value': A33_values[-1],
        'relative_change_percent': relative_changes[-1] if relative_changes else 0,
        'recommended_panels': panel_counts[-1] if converged else 'Increase further'
    }

# Example
panel_counts = [1000, 2000, 5000, 10000, 15000]
A_results = [
    np.diag([15000, 15000, 45000, 1e6, 1e6, 5e5]),
    np.diag([15000, 15000, 48000, 1e6, 1e6, 5e5]),
    np.diag([15000, 15000, 49500, 1e6, 1e6, 5e5]),
    np.diag([15000, 15000, 50000, 1e6, 1e6, 5e5]),
    np.diag([15000, 15000, 50100, 1e6, 1e6, 5e5])
]

convergence = check_added_mass_convergence(panel_counts, A_results)
print(f"Converged: {convergence['converged']}")
print(f"Recommended panels: {convergence['recommended_panels']}")
```
