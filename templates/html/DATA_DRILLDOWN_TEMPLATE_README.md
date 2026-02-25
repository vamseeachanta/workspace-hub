# Interactive Data Drilldown Template

## Overview

This template provides a standardized approach for creating interactive HTML reports with data drilldown capabilities across all workspace-hub repositories.

## Key Features

✅ **Phased Data Loading**: Separate CSV data files loaded asynchronously
✅ **Client-side Pagination**: Display 25 records per page for optimal performance
✅ **Interactive Drilldown**: Modal dialogs for detailed incident/record viewing
✅ **Plotly Visualizations**: Interactive charts with zoom, pan, and export
✅ **Responsive Design**: Mobile-friendly layout
✅ **Performance Optimized**: Reduces file sizes from 100MB+ to <1MB

## Performance Impact

**Before optimization:**
- File size: 100MB+ (all data embedded in HTML)
- Load time: Very slow, browser may hang
- Data: All records embedded in JavaScript onclick handlers

**After optimization:**
- HTML file: <1MB (template only)
- CSV data: Separate files loaded on demand
- Load time: Fast initial load
- Pagination: 25 records at a time

**Example:** Marine safety reports reduced from 107MB to <1MB (97% reduction)

## Usage

### 1. Export Data to CSV

```python
def export_to_csv(df: pd.DataFrame, output_file: str):
    """Export dataframe to CSV for client-side loading."""
    df.to_csv(output_file, index=False, encoding='utf-8')
    return output_file
```

### 2. Generate HTML Report

```python
from pathlib import Path

# Use the template with your data
csv_relative_path = '../../data/results/your_data.csv'
title = "Your Report Title"

# The template handles:
# - Loading CSV via PapaParse
# - Pagination (25 records/page)
# - Modal dialogs for drilldown
# - Interactive visualizations
```

### 3. Required Libraries (CDN)

```html
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>
```

## Template Structure

```
templates/
└── html/
    ├── DATA_DRILLDOWN_TEMPLATE_README.md  # This file
    ├── base_template.html                 # Base HTML structure
    └── examples/
        └── marine_safety_example.py       # Example implementation
```

## Integration Example

See `examples/marine_safety_example.py` for a complete implementation showing:
- CSV data export
- HTML template generation
- Custom column headers
- Visualization integration
- Modal dialog customization

## Cross-Repository Usage

This template is designed to be used across all repositories in workspace-hub:
- `worldenergydata`: Marine safety incident reports
- `energy-analysis`: Production data analysis
- `market-research`: Market trend reports
- Any repository needing interactive data reports

## Customization Points

1. **Column Headers**: Define based on data type
2. **Extra Column Logic**: Custom logic per record type
3. **Modal Content**: Customize fields displayed
4. **Visualization**: Add Plotly charts as needed
5. **Styling**: Modify CSS for branding

## Benefits

✅ **Consistency**: Same UX across all reports
✅ **Performance**: 97% file size reduction
✅ **Maintainability**: Single template to update
✅ **Reusability**: Works for any tabular data
✅ **User Experience**: Fast, intuitive, interactive

## Created

- Date: October 23, 2025
- Original Use Case: Marine safety incident reports (191 incidents, 107MB → <1MB)
- Applied Pattern: CSV data export + client-side loading + pagination

## See Also

- Full implementation: `worldenergydata/scripts/marine_safety/generate_incident_report.py`
- Performance summary: `worldenergydata/results/modules/marine_safety/README.md`
