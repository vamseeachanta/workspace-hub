---
name: html-reporting-enforcer
version: "1.0.0"
category: coordination
description: "HTML Reporting Standards Enforcer"
---

# HTML Reporting Standards Enforcer

> **Version:** 1.0.0
> **Created:** 2026-01-05
> **Category:** workspace-hub
> **Priority:** MANDATORY
> **Related Skills:** development-workflow-orchestrator, knowledge-base-system

## Overview

Enforces HTML_REPORTING_STANDARDS.md across all repositories - ensuring ONLY interactive visualizations (Plotly, Bokeh, Altair, D3.js) are used. NO static matplotlib/seaborn exports allowed.

## Core Rules (MANDATORY)

### ✅ ALLOWED:
- **Plotly** (Python/JS) - Interactive plots with hover, zoom, pan
- **Bokeh** (Python) - Complex dashboards, real-time updates
- **Altair** (Python) - Declarative, grammar-of-graphics
- **D3.js** (JavaScript) - Custom interactive visualizations

### ❌ NOT ALLOWED:
- Static matplotlib PNG/SVG exports
- Seaborn static images
- Any non-interactive plots

## Quick Validation

```python
def validate_visualization(config):
    """Enforce HTML reporting standards."""
    allowed = ['plotly', 'bokeh', 'altair', 'd3']

    if config['visualization_library'] not in allowed:
        raise StandardsViolation(
            f"HTML_REPORTING_STANDARDS.md violation!\n"
            f"Found: {config['visualization_library']}\n"
            f"MUST use: {', '.join(allowed)}\n"
            f"Interactive plots ONLY - no static exports!"
        )

    if not config.get('interactive', True):
        raise StandardsViolation(
            "Interactive mode MUST be enabled for all visualizations"
        )
```

## Standard HTML Report Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis Report - [Module Name]</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .report-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .plot-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="report-header">
        <h1>Analysis Report</h1>
        <p>Generated: <span id="timestamp"></span></p>
        <p>Repository: [Repository Name]</p>
    </div>

    <div class="plot-container">
        <h2>Interactive Analysis</h2>
        <div id="plot1"></div>
    </div>

    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script>
        document.getElementById('timestamp').textContent =
            new Date().toLocaleString();

        // Interactive Plotly plot
        Plotly.newPlot('plot1', [{
            x: [1, 2, 3, 4, 5],
            y: [1, 4, 9, 16, 25],
            mode: 'lines+markers',
            type: 'scatter'
        }], {
            title: 'Interactive Plot',
            hovermode: 'closest'
        }, {
            responsive: true
        });
    </script>
</body>
</html>
```

## Plotly Quick Start

```python
import plotly.express as px
import pandas as pd

# Load data from CSV (relative path)
df = pd.read_csv('../data/processed/results.csv')

# Create interactive plot
fig = px.scatter(df, x='time', y='value',
                 color='category',
                 title='Interactive Analysis',
                 hover_data=['additional_info'])

# Customize for professional appearance
fig.update_layout(
    template='plotly_white',
    hovermode='x unified',
    height=600
)

# Save as standalone HTML
fig.write_html('../reports/analysis_report.html',
               include_plotlyjs='cdn',
               config={'responsive': True})
```

## CSV Data Requirements

**MANDATORY:** Use relative paths from report location

```python
# ✅ CORRECT: Relative path
df = pd.read_csv('../data/processed/results.csv')

# ❌ WRONG: Absolute path
df = pd.read_csv('/mnt/github/workspace-hub/repo/data/results.csv')
```

## Pre-Implementation Check

Before generating ANY visualization:

```python
checklist = {
    "library": "plotly",  # or bokeh, altair, d3
    "interactive": True,
    "hover_tooltips": True,
    "zoom_pan": True,
    "responsive": True,
    "csv_path": "relative",
    "no_static_exports": True
}

validate_reporting_standards(checklist)
```

## Common Violations and Fixes

### ❌ Violation 1: Using matplotlib

```python
# WRONG - Static matplotlib
import matplotlib.pyplot as plt
plt.plot(x, y)
plt.savefig('plot.png')
```

```python
# CORRECT - Interactive Plotly
import plotly.express as px
fig = px.line(df, x='x', y='y')
fig.write_html('report.html')
```

### ❌ Violation 2: Absolute paths

```python
# WRONG - Absolute path
df = pd.read_csv('/home/user/data.csv')
```

```python
# CORRECT - Relative path
df = pd.read_csv('../data/processed/data.csv')
```

## Integration with Workflow

```yaml
# config/input/feature.yaml
output:
  format: "html"
  visualization: "plotly"  # MANDATORY: plotly, bokeh, altair, or d3
  interactive: true        # MANDATORY: must be true
  standalone: true
  csv_data_path: "../data/processed/results.csv"  # Relative path
```

## Enforcement in CI/CD

```yaml
# .github/workflows/validate-reports.yml
- name: Validate HTML Reports
  run: |
    python scripts/validate_html_standards.py
    # Fails if static plots found
```

---

**CRITICAL: Interactive plots ONLY. No exceptions!** 📊
