---
name: engineering-report-generator-example-1-production-analysis-report
description: 'Sub-skill of engineering-report-generator: Example 1: Production Analysis
  Report (+2).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Example 1: Production Analysis Report (+2)

## Example 1: Production Analysis Report


```python
# Configuration
report_config = {
    'title': 'Monthly Production Analysis',
    'project': 'Field A Development',
    'summary': '''
        <div class="summary-grid">
            <div class="metric-card">
                <div class="metric-value">125,000</div>
                <div class="metric-label">Total Oil (bbl)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">98.5%</div>
                <div class="metric-label">Uptime</div>
            </div>
        </div>
    ''',
    'charts': [
        {'type': 'line', 'x': 'date', 'y': 'production', 'title': 'Daily Production'},
        {'type': 'bar', 'x': 'well', 'y': 'cumulative', 'title': 'Well Performance'}
    ]
}

# Generate
generate_report(
    data_path='../data/processed/production.csv',
    output_path='../reports/production_report.html',
    **report_config
)
```


## Example 2: Structural Analysis Report


```python
report_config = {
    'title': 'Structural Analysis Results',
    'methodology': '<p>Analysis performed per DNV-RP-C201 using finite element method.</p>',
    'charts': [
        {'type': 'heatmap', 'x': 'x_coord', 'y': 'y_coord', 'values': 'stress', 'title': 'Stress Distribution'},
        {'type': 'scatter', 'x': 'load', 'y': 'displacement', 'title': 'Load-Displacement Curve'}
    ],
    'conclusions': '<p>All structural elements satisfy design criteria with safety factor > 1.5</p>'
}
```


## Example 3: Multi-Panel Dashboard


```python
from plotly.subplots import make_subplots

def create_dashboard(df: pd.DataFrame, output_path: str):
    """Create multi-panel analysis dashboard."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Trend', 'Distribution', 'Comparison', 'Correlation')
    )

    # Add traces to each panel
    fig.add_trace(go.Scatter(x=df['date'], y=df['value'], mode='lines'), row=1, col=1)
    fig.add_trace(go.Histogram(x=df['value']), row=1, col=2)
    fig.add_trace(go.Bar(x=df['category'], y=df['count']), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['x'], y=df['y'], mode='markers'), row=2, col=2)

    fig.update_layout(height=800, title_text="Analysis Dashboard")
    fig.write_html(output_path)

    return output_path
```
