---
name: plotly-1-javascript-implementation
description: 'Sub-skill of plotly: 1. JavaScript Implementation (+1).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# 1. JavaScript Implementation (+1)

## 1. JavaScript Implementation


#### Basic Line Chart
```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
</head>
<body>
  <div id="chart"></div>
  <script>
    const trace = {
      x: [1, 2, 3, 4, 5],
      y: [10, 15, 13, 17, 20],
      type: 'scatter',
      mode: 'lines+markers',
      marker: { color: 'rgb(219, 64, 82)', size: 12 },
      line: { color: 'rgb(55, 128, 191)', width: 3 }
    };

    const layout = {
      title: 'Interactive Line Chart',
      xaxis: { title: 'X Axis' },
      yaxis: { title: 'Y Axis' },
      hovermode: 'closest'
    };

    Plotly.newPlot('chart', [trace], layout, {
      responsive: true,
      displayModeBar: true
    });
  </script>
</body>
</html>
```

#### Multiple Traces
```javascript
const trace1 = {
  x: [1, 2, 3, 4, 5],
  y: [1, 6, 3, 6, 8],
  type: 'scatter',
  mode: 'lines',
  name: 'Series 1'
};

const trace2 = {
  x: [1, 2, 3, 4, 5],
  y: [5, 1, 6, 9, 2],
  type: 'scatter',
  mode: 'lines+markers',
  name: 'Series 2'
};

const layout = {
  title: 'Multi-Series Chart',
  showlegend: true,
  legend: { x: 1, y: 1 }
};

Plotly.newPlot('chart', [trace1, trace2], layout);
```


## 2. Python Implementation


#### Quick Start with Plotly Express
```python
import plotly.express as px
import pandas as pd

# Load data from CSV
df = pd.read_csv('../data/processed/results.csv')

# Create interactive scatter plot
fig = px.scatter(
    df,
    x='time',
    y='value',
    color='category',
    size='magnitude',
    hover_data=['additional_info'],
    title='Interactive Analysis Results'
)

# Customize layout
fig.update_layout(
    template='plotly_white',
    hovermode='x unified',
    height=600,
    font=dict(size=12)
)

# Save as HTML
fig.write_html('../reports/analysis_plot.html')

# Or display in Jupyter
fig.show()
```

#### Plotly Graph Objects (More Control)
```python
import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv('../data/processed/timeseries.csv')

fig = go.Figure()

# Add trace
fig.add_trace(go.Scatter(
    x=df['date'],
    y=df['value'],
    mode='lines+markers',
    name='Value',
    line=dict(color='rgb(55, 128, 191)', width=2),
    marker=dict(size=8, color='rgb(219, 64, 82)'),
    hovertemplate='<b>Date</b>: %{x}<br>' +
                  '<b>Value</b>: %{y:.2f}<br>' +
                  '<extra></extra>'
))

# Update layout
fig.update_layout(
    title='Time Series Analysis',
    xaxis_title='Date',
    yaxis_title='Value',
    template='plotly_dark',
    hovermode='x unified'
)

fig.write_html('../reports/timeseries.html')
```
