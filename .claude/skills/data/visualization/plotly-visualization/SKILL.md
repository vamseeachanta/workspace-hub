---

name: plotly-visualization
version: "1.0.0"
category: data
description: "Generate interactive Plotly and Matplotlib visualizations from DataFrames with configurable templates and multi-format support."
type: reference
globs:
  - src/assetutilities/common/visualization/**
  - src/assetutilities/common/visualizations.py
  - src/assetutilities/common/visualization.py
alwaysApply: false
tags: []
scripts_exempt: true
---

# Plotly Visualization Skill

## Overview

This skill provides comprehensive visualization capabilities using both Plotly (interactive) and Matplotlib (static) backends. It enables generation of line plots, scatter plots, polar plots, bar charts, timelines, and multi-series visualizations from pandas DataFrames with YAML-driven configuration.

## Key Components

### Visualization Class (visualizations.py)
Main matplotlib-based visualization engine:
- `generate_time_line(data, plt_settings)` - Create timeline visualizations from DataFrame
- `from_df_array(df_array, plt_settings)` - Plot multiple DataFrames as array
- `from_df_columns(df, plt_settings)` - Generate line, scatter, polar, or bar plots from DataFrame columns

### VisualizationTemplatesPlotly (visualization_templates_plotly.py)
Plotly template generator for interactive charts:
- `get_xy_line_df(custom_analysis_dict)` - XY line plot templates
- `get_x_datetime_input_plotly(custom_analysis_dict)` - DateTime-based plot templates

### Specialized Modules
- `visualization_xy.py` - XY coordinate plotting
- `visualization_polar.py` - Polar coordinate systems
- `visualization_common.py` - Shared utilities

## Usage Patterns

### Public-facing risk / incident infographics

When generating infographic statistics from incident, safety, reliability, or risk datasets, treat the evidence taxonomy as part of the visualization contract. Before rendering:

- name each metric with its exact evidence scope;
- persist numerator evidence (`matched_incident_ids`) and exclusions (`excluded_incident_ids`);
- show denominators alongside percentages;
- avoid broad substring classifiers that can overcount (`weather`, `sank`, `overboard` are common traps);
- include caveats in both stats JSON and rendered HTML;
- run adversarial review on metric semantics before merging or publishing.

See `references/risk-infographic-evidence-taxonomy.md` for the checklist and false-positive examples.

### YAML Configuration Structure
```yaml
visualization:
  type: line  # line, scatter, polar, bar
  x_column: timestamp
  y_columns:
    - value1
    - value2
  title: "Analysis Results"
  interactive: true  # Use Plotly vs Matplotlib
```

### Common Workflows
1. **Line Plot from DataFrame**: Load CSV/Excel → Configure columns → Generate plot
2. **Multi-Series Visualization**: Prepare df_array → Set plt_settings → Render combined plot
3. **Timeline Generation**: DataFrame with dates → generate_time_line() → Export

## Module Location
- Primary: `src/assetutilities/common/visualizations.py`
- Templates: `src/assetutilities/common/visualization/visualization_templates_plotly.py`
- XY Plots: `src/assetutilities/common/visualization/visualization_xy.py`
- Polar Plots: `src/assetutilities/common/visualization/visualization_polar.py`

## Dependencies
- matplotlib (static plots)
- plotly (interactive plots)
- pandas (DataFrame handling)
- numpy (numerical operations)
