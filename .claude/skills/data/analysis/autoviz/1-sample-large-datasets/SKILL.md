---
name: autoviz-1-sample-large-datasets
description: 'Sub-skill of autoviz: 1. Sample Large Datasets (+3).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. Sample Large Datasets (+3)

## 1. Sample Large Datasets


```python
# GOOD: Use sampling for initial exploration
AV.AutoViz(
    filename="",
    dfte=large_df,
    max_rows_analyzed=50000,  # Sample for speed
    verbose=1
)

# AVOID: Analyzing millions of rows directly
# This will be slow and may crash
```


## 2. Specify Target Variable When Available


```python
# GOOD: Specify target for focused analysis
AV.AutoViz(
    filename="",
    dfte=df,
    depVar="target_column",  # Enables target-specific charts
    verbose=1
)

# LESS USEFUL: No target specified
# Still works but misses target-related insights
```


## 3. Choose Appropriate Chart Format


```python
# For presentations: PNG
chart_format="png"

# For reports/web: HTML
chart_format="html"

# For notebooks: server or bokeh
chart_format="server"

# For scalable graphics: SVG
chart_format="svg"
```


## 4. Organize Output


```python
# GOOD: Save to organized directory
import os
output_dir = f"eda_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(output_dir, exist_ok=True)

AV.AutoViz(
    filename="",
    dfte=df,
    save_plot_dir=output_dir,
    chart_format="png"
)
```
