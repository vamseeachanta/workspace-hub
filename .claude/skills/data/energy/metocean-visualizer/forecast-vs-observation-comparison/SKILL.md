---
name: metocean-visualizer-forecast-vs-observation-comparison
description: 'Sub-skill of metocean-visualizer: Forecast vs Observation Comparison.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Forecast vs Observation Comparison

## Forecast vs Observation Comparison


```python
def plot_forecast_comparison(
    obs_df: pd.DataFrame,
    fcst_df: pd.DataFrame,
    param: str = 'wave_height_m',
    output_path: Optional[str] = None
) -> go.Figure:
    """Compare forecast vs observation time series."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=obs_df['time'], y=obs_df[param],
        name='Observation',
        mode='lines+markers',
        marker=dict(size=4),
        line=dict(color='#1f77b4')
    ))

    fig.add_trace(go.Scatter(
        x=fcst_df['time'], y=fcst_df[param],
        name='Forecast',
        mode='lines',
        line=dict(color='#ff7f0e', dash='dash')
    ))


*See sub-skills for full details.*
