---
name: plotly-example-1-3d-scatter-plot
description: 'Sub-skill of plotly: Example 1: 3D Scatter Plot (+5).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# Example 1: 3D Scatter Plot (+5)

## Example 1: 3D Scatter Plot


```python
import plotly.express as px
import numpy as np

# Generate 3D data
n = 500
x = np.random.randn(n)
y = np.random.randn(n)
z = np.random.randn(n)
colors = np.random.rand(n)

*See sub-skills for full details.*

## Example 2: Statistical Box Plot with Violin


```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

df = pd.read_csv('../data/processed/measurements.csv')

# Create subplots
fig = make_subplots(
    rows=1, cols=2,

*See sub-skills for full details.*

## Example 3: Animated Time Series


```python
import plotly.express as px
import pandas as pd

df = pd.read_csv('../data/processed/timeseries_multi.csv')

fig = px.line(
    df,
    x='date',
    y='value',

*See sub-skills for full details.*

## Example 4: Interactive Heatmap with Annotations


```python
import plotly.graph_objects as go
import numpy as np

# Generate correlation matrix
data = np.random.rand(10, 10)
labels = [f'Var {i+1}' for i in range(10)]

fig = go.Figure(data=go.Heatmap(
    z=data,

*See sub-skills for full details.*

## Example 5: Multi-Axis Chart


```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots

fig = make_subplots(specs=[[{"secondary_y": True}]])

# Temperature (primary y-axis)
fig.add_trace(
    go.Scatter(x=[1, 2, 3, 4, 5], y=[20, 22, 25, 23, 24],
               name="Temperature (°C)", mode='lines+markers'),

*See sub-skills for full details.*

## Example 6: Large Dataset with WebGL


```python
import plotly.graph_objects as go
import numpy as np

# Generate large dataset (100,000 points)
n = 100000
x = np.random.randn(n)
y = np.random.randn(n)

# Use Scattergl for performance

*See sub-skills for full details.*
