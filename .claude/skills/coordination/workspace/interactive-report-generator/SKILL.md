---
name: interactive-report-generator
description: Generate interactive HTML reports with Plotly visualizations from data
  analysis results. Supports dashboards, charts, and professional styling.
version: 1.0.0
category: coordination
type: skill
trigger: manual
auto_execute: false
capabilities:
- plotly_visualization
- html_report_generation
- dashboard_creation
- csv_data_integration
- responsive_design
tools:
- Write
- Read
- Bash
related_skills:
- data-validation-reporter
- yaml-workflow-executor
requires: []
see_also:
- interactive-report-generator-example-1-simple-report
- interactive-report-generator-best-practices
tags: []
---

# Interactive Report Generator

## Quick Start

```bash
# Generate report from data
/interactive-report-generator --data results.csv --output report.html

# Create dashboard
/interactive-report-generator --type dashboard --config dashboard.yaml

# Generate from analysis results
/interactive-report-generator --source analysis_output/
```

## When to Use

**USE when:**
- Creating analysis reports
- Generating data visualizations
- Building dashboards
- Presenting results to stakeholders

**DON'T USE when:**
- Static images are required
- PDF export is primary format
- Real-time streaming data

## Prerequisites

- Python 3.9+
- plotly>=5.15.0
- pandas>=2.0.0
- Data in CSV/DataFrame format

## Overview

Generates interactive HTML reports compliant with workspace-hub HTML_REPORTING_STANDARDS.md:

1. **Interactive plots only** - No static matplotlib
2. **CSV data import** - Relative paths
3. **Responsive design** - Works on all devices
4. **Professional styling** - Consistent theming
5. **Export options** - PNG, SVG from plots

## Core Templates

### 1. Basic Report Template

```python
"""
ABOUTME: Interactive HTML report generator
ABOUTME: Creates Plotly-based reports from analysis data
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

*See sub-skills for full details.*
### 2. Report Generator Class

```python
"""
ABOUTME: Full-featured report generator class
ABOUTME: Supports multiple plot types and configurations
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

*See sub-skills for full details.*

## Execution Checklist

**Data Preparation:**
- [ ] Data loaded as DataFrame
- [ ] Column names are clean
- [ ] Date columns parsed
- [ ] Missing values handled

**Report Creation:**
- [ ] Add data to generator
- [ ] Select appropriate plot types
- [ ] Configure titles and labels
- [ ] Generate HTML output

**Validation:**
- [ ] Open report in browser
- [ ] Verify interactivity works
- [ ] Check responsive design
- [ ] Test export options

## Error Handling

### Missing Columns

```
Error: Column 'value' not found in data

Check:
1. Column names in DataFrame
2. Spelling and case sensitivity
3. Data was loaded correctly
```
### Empty Data

```
Error: No data to plot

Check:
1. DataFrame is not empty
2. Filters not too restrictive
3. Data loading succeeded
```

## Related Skills

- [data-validation-reporter](../data-validation-reporter/SKILL.md) - Data quality reports
- [yaml-workflow-executor](../yaml-workflow-executor/SKILL.md) - Configuration-driven reports

## References

- [Plotly Python Documentation](https://plotly.com/python/)
- [HTML Reporting Standards](../../../docs/modules/standards/HTML_REPORTING_STANDARDS.md)

---

## Version History

- **1.0.0** (2026-01-14): Initial release - Plotly-based interactive HTML report generator with dashboards, multiple plot types, and responsive design

## Sub-Skills

- [Example 1: Simple Report (+2)](example-1-simple-report/SKILL.md)
- [Best Practices](best-practices/SKILL.md)
