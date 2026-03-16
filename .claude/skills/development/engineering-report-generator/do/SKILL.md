---
name: engineering-report-generator-do
description: 'Sub-skill of engineering-report-generator: Do (+4).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Do (+4)

## Do


1. Use relative paths from report location for data
2. Include interactive plots only (Plotly, Bokeh, Altair)
3. Apply consistent color schemes across charts
4. Add clear axis labels and titles
5. Include hover data for detailed values
6. Make reports responsive (mobile-friendly)


## Don't


1. Export static matplotlib PNG/SVG images
2. Use absolute file paths
3. Create overly complex visualizations
4. Skip executive summaries
5. Ignore accessibility (color contrast)


## Data Input

- Use relative paths from report location
- CSV files with clear column headers
- Data pre-processed and validated


## HTML Output

- Self-contained files (CDN for Plotly)
- Responsive design (mobile-friendly)
- Print-friendly styling
- Accessible color contrast


## File Organization

```
project/
    data/
        raw/           # Original data
        processed/     # Analysis-ready CSV
    reports/
        analysis.html  # Generated reports
    scripts/
        generate_report.py
```
