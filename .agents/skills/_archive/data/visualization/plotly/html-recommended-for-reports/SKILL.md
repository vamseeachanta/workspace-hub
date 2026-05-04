---
name: plotly-html-recommended-for-reports
description: 'Sub-skill of plotly: HTML (Recommended for Reports) (+2).'
version: 1.0.0
category: data-visualization
type: reference
scripts_exempt: true
---

# HTML (Recommended for Reports) (+2)

## HTML (Recommended for Reports)


```python
fig.write_html('report.html', include_plotlyjs='cdn')
```

## Static Images


```python
# Requires kaleido
fig.write_image('chart.png', width=1200, height=800)
fig.write_image('chart.pdf')
fig.write_image('chart.svg')
```

## JSON


```python
import json
fig.write_json('chart.json')
```
