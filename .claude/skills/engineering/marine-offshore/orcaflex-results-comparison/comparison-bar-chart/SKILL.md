---
name: orcaflex-results-comparison-comparison-bar-chart
description: 'Sub-skill of orcaflex-results-comparison: Comparison Bar Chart (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Comparison Bar Chart (+1)

## Comparison Bar Chart


```python
import plotly.graph_objects as go

def create_comparison_bar_chart(
    comparison_df: pd.DataFrame,
    variable: str,
    title: str
) -> go.Figure:
    """Create interactive bar chart comparing simulations."""


*See sub-skills for full details.*

## Radar Chart for Multi-Variable Comparison


```python
import plotly.graph_objects as go

def create_radar_comparison(
    stiffness_comparison: dict
) -> go.Figure:
    """Create radar chart for stiffness comparison."""

    categories = ["K_xx", "K_yy", "K_zz", "K_xy", "K_xz", "K_yz"]


*See sub-skills for full details.*
