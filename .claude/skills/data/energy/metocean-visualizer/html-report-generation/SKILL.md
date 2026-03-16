---
name: metocean-visualizer-html-report-generation
description: 'Sub-skill of metocean-visualizer: HTML Report Generation.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# HTML Report Generation

## HTML Report Generation


```python
import plotly.io as pio


def generate_metocean_report(
    df: pd.DataFrame,
    station_info: dict,
    output_path: str = 'reports/metocean_report.html'
) -> str:
    """Generate comprehensive HTML metocean report."""
    builder = MetoceanChartBuilder()

    ts_fig = builder.time_series(df)
    rose_fig = builder.wave_rose(df)
    scatter_fig = builder.scatter_hs_tp(df)

    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Metocean Report - {station_info["id"]}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .plot-container {{ margin: 20px 0; }}
        h1 {{ color: #333; }}

*See sub-skills for full details.*
