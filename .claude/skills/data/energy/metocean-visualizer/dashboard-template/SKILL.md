---
name: metocean-visualizer-dashboard-template
description: 'Sub-skill of metocean-visualizer: Dashboard Template.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Dashboard Template

## Dashboard Template


```python
def create_metocean_dashboard(
    df: pd.DataFrame,
    stations: list,
    output_path: str = 'reports/metocean_dashboard.html'
) -> go.Figure:
    """Create comprehensive metocean dashboard."""
    fig = make_subplots(
        rows=2, cols=2,
        specs=[
            [{"type": "scatter"}, {"type": "polar"}],
            [{"type": "scatter"}, {"type": "scattermapbox"}]
        ],
        subplot_titles=('Time Series', 'Wave Rose', 'Hs vs Tp', 'Station Map'),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )

    # Time series (row 1, col 1)
    fig.add_trace(
        go.Scatter(
            x=df['time'], y=df['wave_height_m'],
            name='Hs', line=dict(color='#1f77b4')
        ),
        row=1, col=1

*See sub-skills for full details.*
