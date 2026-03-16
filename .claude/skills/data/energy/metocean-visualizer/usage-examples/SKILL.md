---
name: metocean-visualizer-usage-examples
description: 'Sub-skill of metocean-visualizer: Usage Examples.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Usage Examples

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
