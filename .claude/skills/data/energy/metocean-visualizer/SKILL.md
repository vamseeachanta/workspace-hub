---
name: metocean-visualizer
description: Create interactive metocean visualizations including time series plots, wave roses, scatter plots, geographic maps, and dashboards. Use for data exploration, reporting, and operational monitoring.
---

# Metocean Visualizer Skill

> Interactive visualization toolkit for metocean data analysis using Plotly

## When to Use This Skill

Use this skill when you need to:
- Plot wave data or create metocean dashboards
- Visualize buoy observations or hindcast data
- Generate wave roses or wind roses
- Create time series charts for Hs, Tp, wind speed
- Build scatter plots (Hs vs Tp, wind vs waves)
- Map metocean stations with interactive overlays
- Compare forecasts vs observations
- Generate joint distribution contour plots
- Create operational monitoring dashboards

**Trigger phrases:**
- "Plot wave data", "Create metocean dashboard"
- "Visualize buoy observations", "Generate wave rose"
- "Time series chart", "Scatter plot Hs vs Tp"
- "Map metocean stations", "Interactive plot"
- "Compare forecasts vs observations"

## Visualization Types

### Time Series Plots
- Single parameter trends (Hs, Tp, wind speed)
- Multi-parameter comparison on shared x-axis
- Quality flag indicators with color coding
- Forecast vs observation overlays

### Directional Roses
- Wave roses (Hs by direction)
- Wind roses (speed by direction)
- Current roses (velocity by direction)
- Customizable sectors (8, 12, 16, 36)

### Scatter Plots
- Hs vs Tp (wave height vs period)
- Wind speed vs wave height correlations
- Joint distribution contours
- Color-coded by time/quality/source

### Geographic Maps
- Station locations with Scattermapbox
- Data overlays (latest values)
- Regional coverage visualization
- Interactive hover details

### Joint Distribution Charts
- 2D histograms (Histogram2d)
- Contour plots for environmental design
- Conditional distributions
- Return period contours

### Statistical Charts
- Histograms with kernel density
- CDFs (cumulative distribution functions)
- QQ plots for distribution comparison
- Box plots by month/season

## Core Patterns

```python
"""
ABOUTME: Interactive visualization toolkit for metocean data analysis
ABOUTME: Provides chart templates for waves, wind, currents, and mapping
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional


class MetoceanChartBuilder:
    """Build interactive metocean charts with Plotly."""

    def time_series(
        self,
        df: pd.DataFrame,
        output_path: Optional[str] = None
    ) -> go.Figure:
        """Create interactive time series of wave parameters."""
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Wave Height', 'Wave Period', 'Wind Speed')
        )

        # Wave height
        fig.add_trace(
            go.Scatter(
                x=df['time'], y=df['wave_height_m'],
                name='Hs', line=dict(color='#1f77b4')
            ),
            row=1, col=1
        )

        # Wave period
        fig.add_trace(
            go.Scatter(
                x=df['time'], y=df['wave_period_s'],
                name='Tp', line=dict(color='#2ca02c')
            ),
            row=2, col=1
        )

        # Wind speed
        fig.add_trace(
            go.Scatter(
                x=df['time'], y=df['wind_speed_ms'],
                name='U10', line=dict(color='#d62728')
            ),
            row=3, col=1
        )

        fig.update_layout(
            height=800,
            title='Metocean Time Series',
            hovermode='x unified'
        )
        fig.update_yaxes(title_text='Hs (m)', row=1, col=1)
        fig.update_yaxes(title_text='Tp (s)', row=2, col=1)
        fig.update_yaxes(title_text='U10 (m/s)', row=3, col=1)

        if output_path:
            fig.write_html(output_path)
        return fig

    def wave_rose(
        self,
        df: pd.DataFrame,
        height_col: str = 'wave_height_m',
        direction_col: str = 'wave_direction_deg',
        n_sectors: int = 16,
        output_path: Optional[str] = None
    ) -> go.Figure:
        """Create interactive wave rose with Plotly."""
        sector_width = 360 / n_sectors
        bins = np.arange(0, 360 + sector_width, sector_width)

        df['dir_bin'] = pd.cut(
            df[direction_col],
            bins=bins,
            labels=bins[:-1] + sector_width / 2
        )

        stats = df.groupby('dir_bin').agg({
            height_col: ['count', 'mean']
        }).reset_index()
        stats.columns = ['direction', 'count', 'mean_hs']
        total = stats['count'].sum()
        stats['occurrence_pct'] = 100 * stats['count'] / total

        fig = go.Figure()
        fig.add_trace(go.Barpolar(
            r=stats['occurrence_pct'],
            theta=stats['direction'],
            width=sector_width * 0.9,
            marker_color=stats['mean_hs'],
            marker_colorscale='Viridis',
            marker_colorbar=dict(title='Hs (m)'),
            hovertemplate=(
                'Direction: %{theta:.0f} deg<br>'
                'Occurrence: %{r:.1f}%<br>'
                'Mean Hs: %{marker.color:.2f} m'
            )
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, stats['occurrence_pct'].max() * 1.1]),
                angularaxis=dict(direction='clockwise', rotation=90)
            ),
            title='Wave Rose',
            showlegend=False
        )

        if output_path:
            fig.write_html(output_path)
        return fig

    def scatter_hs_tp(
        self,
        df: pd.DataFrame,
        output_path: Optional[str] = None
    ) -> go.Figure:
        """Create Hs vs Tp scatter plot with 2D histogram."""
        fig = go.Figure()

        # 2D histogram background
        fig.add_trace(go.Histogram2d(
            x=df['wave_height_m'],
            y=df['wave_period_s'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title='Count'),
            nbinsx=50,
            nbinsy=50
        ))

        # Scatter overlay for detail
        fig.add_trace(go.Scatter(
            x=df['wave_height_m'],
            y=df['wave_period_s'],
            mode='markers',
            marker=dict(size=3, color='white', opacity=0.3),
            hovertemplate='Hs: %{x:.2f} m<br>Tp: %{y:.1f} s'
        ))

        fig.update_layout(
            xaxis_title='Significant Wave Height (m)',
            yaxis_title='Peak Wave Period (s)',
            title='Hs vs Tp Joint Distribution'
        )

        if output_path:
            fig.write_html(output_path)
        return fig

    def station_map(
        self,
        stations: list,
        output_path: Optional[str] = None
    ) -> go.Figure:
        """Create interactive map of metocean stations."""
        lats = [s['latitude'] for s in stations]
        lons = [s['longitude'] for s in stations]
        names = [s['station_id'] for s in stations]

        fig = go.Figure(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='markers',
            marker=dict(size=12, color='#1f77b4'),
            text=names,
            hovertemplate='%{text}<br>Lat: %{lat:.3f}<br>Lon: %{lon:.3f}'
        ))

        fig.update_layout(
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=sum(lats) / len(lats), lon=sum(lons) / len(lons)),
                zoom=5
            ),
            title='Metocean Stations',
            margin=dict(l=0, r=0, t=40, b=0)
        )

        if output_path:
            fig.write_html(output_path)
        return fig
```

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
    )

    # Wave rose (row 1, col 2)
    dir_stats = calculate_directional_stats(df)
    fig.add_trace(
        go.Barpolar(
            r=dir_stats['occurrence_pct'],
            theta=dir_stats['direction'],
            marker_color=dir_stats['mean_hs'],
            marker_colorscale='Viridis'
        ),
        row=1, col=2
    )

    # Scatter plot (row 2, col 1)
    fig.add_trace(
        go.Scatter(
            x=df['wave_height_m'], y=df['wave_period_s'],
            mode='markers', marker=dict(size=4, opacity=0.5),
            name='Hs vs Tp'
        ),
        row=2, col=1
    )

    # Map (row 2, col 2)
    fig.add_trace(
        go.Scattermapbox(
            lat=[s['latitude'] for s in stations],
            lon=[s['longitude'] for s in stations],
            mode='markers',
            marker=dict(size=10),
            text=[s['station_id'] for s in stations]
        ),
        row=2, col=2
    )

    fig.update_layout(
        height=900,
        title='Metocean Dashboard',
        mapbox=dict(style='open-street-map', zoom=4)
    )
    fig.write_html(output_path)
    return fig


def calculate_directional_stats(df: pd.DataFrame, n_sectors: int = 16) -> pd.DataFrame:
    """Calculate directional statistics for rose plots."""
    sector_width = 360 / n_sectors
    bins = np.arange(0, 360 + sector_width, sector_width)

    df_copy = df.copy()
    df_copy['dir_bin'] = pd.cut(
        df_copy['wave_direction_deg'],
        bins=bins,
        labels=bins[:-1] + sector_width / 2
    )

    stats = df_copy.groupby('dir_bin').agg({
        'wave_height_m': ['count', 'mean']
    }).reset_index()
    stats.columns = ['direction', 'count', 'mean_hs']
    total = stats['count'].sum()
    stats['occurrence_pct'] = 100 * stats['count'] / total

    return stats
```

## Wind Rose with Matplotlib (windrose package)

```python
from windrose import WindroseAxes
import matplotlib.pyplot as plt
import numpy as np


def plot_wind_rose_matplotlib(
    speeds: np.ndarray,
    directions: np.ndarray,
    output_path: Optional[str] = None,
    title: str = 'Wind Rose'
) -> plt.Figure:
    """Create wind rose diagram using windrose package."""
    fig = plt.figure(figsize=(10, 10))
    ax = WindroseAxes.from_ax(fig=fig)
    ax.bar(
        directions, speeds,
        normed=True, opening=0.8,
        bins=np.arange(0, 25, 5),
        cmap=plt.cm.viridis
    )
    ax.set_legend(title='Speed (m/s)')
    ax.set_title(title)

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
    return fig
```

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

    fig.update_layout(
        title=f'{param} - Forecast vs Observation',
        xaxis_title='Time',
        yaxis_title=param,
        hovermode='x unified',
        legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01)
    )

    if output_path:
        fig.write_html(output_path)
    return fig
```

## HTML Report Generation

```python
import plotly.io as pio


def generate_metocean_report(
    df: pd.DataFrame,
    station_info: dict,
    output_path: str = 'reports/metocean_report.html'
) -> str:
    """Generate comprehensive HTML metocean report."""
    builder = MetoceanChartBuilder()

    ts_fig = builder.time_series(df)
    rose_fig = builder.wave_rose(df)
    scatter_fig = builder.scatter_hs_tp(df)

    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Metocean Report - {station_info["id"]}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .plot-container {{ margin: 20px 0; }}
        h1 {{ color: #333; }}
        h2 {{ color: #555; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        .metadata {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
        .metadata p {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <h1>Metocean Report: Station {station_info["id"]}</h1>
    <div class="metadata">
        <p><strong>Location:</strong> {station_info["lat"]:.3f} N, {station_info["lon"]:.3f} W</p>
        <p><strong>Period:</strong> {df["time"].min()} to {df["time"].max()}</p>
        <p><strong>Records:</strong> {len(df):,}</p>
        <p><strong>Data Source:</strong> {station_info.get("source", "N/A")}</p>
    </div>

    <h2>Time Series</h2>
    <div class="plot-container">
        {pio.to_html(ts_fig, include_plotlyjs=False, full_html=False)}
    </div>

    <h2>Wave Rose</h2>
    <div class="plot-container">
        {pio.to_html(rose_fig, include_plotlyjs=False, full_html=False)}
    </div>

    <h2>Joint Distribution</h2>
    <div class="plot-container">
        {pio.to_html(scatter_fig, include_plotlyjs=False, full_html=False)}
    </div>
</body>
</html>'''

    with open(output_path, 'w') as f:
        f.write(html_content)

    return output_path
```

## Usage Examples

```python
from worldenergydata.metocean.visualize import MetoceanChartBuilder
import pandas as pd

# Load data
df = pd.read_csv('data/processed/buoy_data.csv', parse_dates=['time'])

# Create individual charts
builder = MetoceanChartBuilder()

# Time series
fig_ts = builder.time_series(df)
fig_ts.write_html('reports/time_series.html')

# Wave rose
fig_rose = builder.wave_rose(df)
fig_rose.write_html('reports/wave_rose.html')

# Scatter plot
fig_scatter = builder.scatter_hs_tp(df)
fig_scatter.write_html('reports/scatter_hs_tp.html')

# Station map
stations = [
    {'station_id': 'NDBC-41001', 'latitude': 34.68, 'longitude': -72.66},
    {'station_id': 'NDBC-41002', 'latitude': 31.76, 'longitude': -74.84}
]
fig_map = builder.station_map(stations)
fig_map.write_html('reports/station_map.html')

# Generate full report
generate_metocean_report(df, {'id': 'NDBC-41001', 'lat': 34.68, 'lon': -72.66})
```

## External Tool Integration

**windrose package (for matplotlib roses):**
```bash
pip install windrose
```

**MetOceanViewer Patterns (Desktop Reference):**
- Map-based station selection
- Time series with multiple y-axes
- Model-observation comparison panels
- Geographic data overlays

## Best Practices

1. **Always use interactive plots** - Plotly preferred for web-based reports
2. **Include hover information** - Provide relevant data on all points
3. **Use relative paths** - Store data in `/data/raw/` or `/data/processed/`
4. **Consistent color schemes** - Use same colors across related plots
5. **Include metadata** - Station info, time range, data source
6. **Export standalone HTML** - Embed Plotly.js for portability
7. **Optimize for both screen and print** - Consider responsive layouts

## Output Formats

| Format | Use Case | Method |
|--------|----------|--------|
| Interactive HTML | Web dashboards, reports | `fig.write_html()` |
| PNG/SVG | Static reports, publications | `fig.write_image()` |
| JSON | Data interchange | `fig.to_json()` |
| Dashboard HTML | Multi-panel views | `make_subplots()` |

## Common Workflows

1. **Station Overview**: Fetch data -> Time series + Rose + Map -> HTML report
2. **Comparison Dashboard**: Multiple stations -> Side-by-side plots -> Export
3. **Operational Monitoring**: Real-time fetch -> Update dashboard -> Alert thresholds
4. **Design Analysis**: Joint distributions -> Environmental contours -> Export

## Related Skills

- `energy-data-visualizer` - General energy visualization patterns
- `metocean-data-fetcher` - Data source for visualization
- `metocean-statistics` - Statistical analysis for contours
