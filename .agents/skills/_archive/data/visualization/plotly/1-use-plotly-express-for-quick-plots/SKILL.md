---
name: plotly-1-use-plotly-express-for-quick-plots
description: 'Sub-skill of plotly: 1. Use Plotly Express for Quick Plots (+4).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# 1. Use Plotly Express for Quick Plots (+4)

## 1. Use Plotly Express for Quick Plots

```python
# Simple and readable
fig = px.scatter(df, x='x', y='y', color='category', title='Quick Scatter')
```


## 2. Graph Objects for Complex Customization

```python
# More control
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode='markers'))
fig.update_layout(title='Custom Chart')
```


## 3. Optimize for Large Datasets

```python
# Use Scattergl for >10k points
fig = go.Figure(data=go.Scattergl(x=x, y=y, mode='markers'))
```


## 4. Responsive Design

```python
fig.update_layout(
    autosize=True,
    margin=dict(l=20, r=20, t=40, b=20)
)
```


## 5. Custom Hover Templates

```python
fig.update_traces(
    hovertemplate='<b>%{x}</b><br>Value: %{y:.2f}<extra></extra>'
)
```
