---
name: interactive-report-generator-example-1-simple-report
description: 'Sub-skill of interactive-report-generator: Example 1: Simple Report
  (+2).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Example 1: Simple Report (+2)

## Example 1: Simple Report


```python
import pandas as pd
from pathlib import Path
from report_generator import InteractiveReportGenerator

# Load data
df = pd.read_csv('data/analysis_results.csv')

# Create report
report = InteractiveReportGenerator()
report.add_data(df)
report.add_time_series('date', ['value1', 'value2'])
report.add_histogram('value1')
report.add_heatmap()

# Generate
output = report.generate(
    Path('reports/analysis_report.html'),
    title='Analysis Results'
)
print(f"Report saved: {output}")
```


## Example 2: Dashboard Creation


```python
# Create dashboard with multiple views
report = InteractiveReportGenerator()
report.add_data(df)

# Add various plots
report.add_time_series('timestamp', ['metric_a', 'metric_b'])
report.add_scatter_plot('x_value', 'y_value', color_col='category')
report.add_bar_chart('category', 'total')
report.add_histogram('distribution_col')

# Generate dashboard
report.generate(
    Path('reports/dashboard.html'),
    title='Project Dashboard'
)
```


## Example 3: From CLI


```bash
# Generate report from command line
python -m report_generator \
    --data results.csv \
    --output report.html \
    --title "Analysis Results" \
    --plots time_series histogram heatmap
```
