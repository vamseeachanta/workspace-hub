---
name: engineering-report-generator
description: Generate engineering analysis reports with interactive Plotly visualizations,
  standard report sections, and HTML export. Use for creating dashboards, analysis
  summaries, and technical documentation with charts.
type: reference
version: 1.1.0
category: development
related_skills:
- data-pipeline-processor
- yaml-workflow-executor
- parallel-file-processor
capabilities: []
requires: []
tags: []
freedom: medium
---

# Engineering Report Generator

## Quick Start

```python
import plotly.express as px
import pandas as pd
from pathlib import Path
from datetime import datetime

# Load data
df = pd.read_csv("../data/processed/results.csv")

# Create visualization
fig = px.line(df, x="date", y="value", title="Analysis Results")

# Generate HTML report
html = f"""<!DOCTYPE html>
<html>
<head><title>Engineering Report</title></head>
<body>
<h1>Analysis Report - {datetime.now().strftime('%Y-%m-%d')}</h1>
{fig.to_html(full_html=False, include_plotlyjs="cdn")}
</body>
</html>"""

Path("../reports/analysis.html").write_text(html)
print("Report generated: reports/analysis.html")
```

## When to Use

- Creating analysis reports with charts and visualizations
- Building interactive dashboards from CSV/data sources
- Generating technical documentation with plots
- Producing client-deliverable HTML reports
- Summarizing engineering calculations with graphics

## Report Structure

### Standard Sections

1. **Header** - Title, date, project info, version
2. **Executive Summary** - Key findings and metrics at a glance
3. **Methodology** - Analysis approach and assumptions
4. **Results** - Data tables and interactive visualizations
5. **Discussion** - Interpretation of results
6. **Conclusions** - Summary and recommendations
7. **Appendix** - Supporting data, references

## Implementation Pattern

### Basic Report Generation

```python
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path
from datetime import datetime

def generate_report(
    data_path: str,

*See sub-skills for full details.*
### Visualization Patterns

```python
def create_visualizations(df: pd.DataFrame, chart_configs: list) -> list:
    """Create Plotly figures from configuration."""
    figures = []

    for config in chart_configs:
        chart_type = config.get('type', 'line')

        if chart_type == 'line':
            fig = px.line(

*See sub-skills for full details.*
### HTML Template

```python
def build_html_report(title: str, sections: dict, figures: list) -> str:
    """Build complete HTML report."""

    # Convert figures to HTML
    chart_html = '\n'.join([
        f'<div class="chart-container">{fig.to_html(full_html=False, include_plotlyjs="cdn")}</div>'
        for fig in figures
    ])


*See sub-skills for full details.*

## Integration

### With YAML Workflow

```yaml
task: generate_report
input:
  data_path: data/processed/results.csv
output:
  report_path: reports/analysis.html
config:
  title: "Analysis Report"
  charts:
    - type: line
      x: time
      y: value
```
### With Data Pipeline

```python
# Pipeline output -> Report input
pipeline_results = process_data(raw_data)
pipeline_results.to_csv('data/processed/results.csv')

generate_report(
    data_path='data/processed/results.csv',
    output_path='reports/analysis.html',
    title='Pipeline Results'
)
```

## Related Skills

- [xlsx](../../document-handling/xlsx/SKILL.md) - Excel data handling
- [pdf](../../document-handling/pdf/SKILL.md) - PDF report generation
- [data-pipeline-processor](../data-pipeline-processor/SKILL.md) - Data preparation
- [yaml-workflow-executor](../yaml-workflow-executor/SKILL.md) - Workflow automation

---

## Version History

- **1.1.0** (2026-01-02): Upgraded to SKILL_TEMPLATE_v2 format with Quick Start, Error Handling, Metrics, Execution Checklist, additional examples
- **1.0.0** (2024-10-15): Initial release with Plotly visualizations, HTML templates, responsive design

## Sub-Skills

- [Example 1: Production Analysis Report (+2)](example-1-production-analysis-report/SKILL.md)
- [Do (+4)](do/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Metrics](metrics/SKILL.md)
