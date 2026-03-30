---
name: plotly-with-pandas
description: 'Sub-skill of plotly: With Pandas (+2).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# With Pandas (+2)

## With Pandas

```python
import plotly.express as px
df = pd.read_csv('data.csv')
fig = px.line(df, x='date', y='value')
```


## With NumPy

```python
import numpy as np
import plotly.graph_objects as go

x = np.linspace(0, 10, 100)
y = np.sin(x)

fig = go.Figure(data=go.Scatter(x=x, y=y))
```


## With Jupyter Notebooks

```python
# Automatically displays in cell output
fig.show()

# Or use widget mode
import plotly.graph_objects as go
fig = go.FigureWidget()
```
