---
name: plotly-built-in-templates
description: 'Sub-skill of plotly: Built-in Templates (+1).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# Built-in Templates (+1)

## Built-in Templates


```python
# Available templates: plotly, plotly_white, plotly_dark, ggplot2, seaborn, simple_white
fig.update_layout(template='plotly_dark')
```

## Custom Theme


```python
custom_template = go.layout.Template(
    layout=dict(
        font=dict(family='Arial', size=14),
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='white'
    )
)

fig.update_layout(template=custom_template)
```

---

**Use this skill for professional, interactive scientific and analytical visualizations with minimal code!**
