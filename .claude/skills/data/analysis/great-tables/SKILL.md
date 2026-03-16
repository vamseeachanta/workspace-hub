---
name: great-tables
version: 1.0.0
description: Publication-quality tables in Python with rich styling, formatting, conditional
  formatting, and export to HTML/images - inspired by R's gt package
author: workspace-hub
category: data-analysis
capabilities:
- Publication-quality table rendering
- Rich styling and formatting options
- Conditional formatting with colors and icons
- Grouped rows and columns
- Spanner headers and footnotes
- Export to HTML, PNG, and PDF
- Integration with pandas and polars
- Interactive HTML output
tools:
- great_tables
- pandas
- polars
- webshot
tags:
- great-tables
- tables
- formatting
- publication
- styling
- conditional-formatting
- html-tables
- data-presentation
- reporting
platforms:
- python
related_skills:
- pandas-data-processing
- polars
- ydata-profiling
- streamlit
- plotly
requires: []
see_also:
- great-tables-1-basic-table-creation
- great-tables-2-column-formatting
- great-tables-3-styling-and-colors
- great-tables-4-conditional-formatting
- great-tables-5-grouped-rows-and-columns
- great-tables-6-footnotes-and-annotations
- great-tables-great-tables-with-streamlit
- great-tables-1-keep-tables-focused
- great-tables-common-issues
scripts_exempt: true
---

# Great Tables

## When to Use This Skill

### USE Great Tables when:

- **Publication tables** - Creating tables for reports, papers, or presentations
- **Data presentation** - Professional display of analysis results
- **Conditional formatting** - Highlighting patterns with colors and icons
- **Complex layouts** - Multi-level headers, grouped rows, footnotes
- **HTML reports** - Interactive tables for web-based reports
- **Quick formatting** - Need polished tables without manual styling
- **Dashboard components** - Tables in Streamlit/Dash applications
- **Export requirements** - Need PNG or PDF output
### DON'T USE Great Tables when:

- **Large datasets** - Over 1000 rows for display (use pagination)
- **Interactive editing** - Need editable cells (use Streamlit data_editor)
- **Real-time updates** - Streaming data display
- **Complex interactivity** - Sorting, filtering (use DataTables or AG Grid)
- **Raw data exploration** - Use pandas display or ydata-profiling

## Prerequisites

```bash
# Basic installation
pip install great_tables

# With all optional dependencies
pip install great_tables pandas polars

# For image export (PNG/PDF)
pip install great_tables webshot

# Using uv (recommended)
uv pip install great_tables pandas polars

# Verify installation
python -c "from great_tables import GT; print('Great Tables ready!')"
```

## Complete Examples

### Example 1: Financial Report Table

```python
from great_tables import GT, html
from great_tables import style, loc
import pandas as pd
import numpy as np

def create_financial_report(
    data: pd.DataFrame,
    title: str = "Financial Report",
    output_path: str = "financial_report.html"

*See sub-skills for full details.*
### Example 2: Sales Dashboard Table

```python
from great_tables import GT, html
from great_tables import style, loc
import pandas as pd
import numpy as np

def create_sales_dashboard_table(output_path: str = "sales_dashboard.html") -> GT:
    """
    Create sales dashboard table with KPIs and sparklines.
    """

*See sub-skills for full details.*
### Example 3: Scientific Data Table

```python
from great_tables import GT
from great_tables import style, loc
import pandas as pd
import numpy as np

def create_scientific_table(output_path: str = "scientific_table.html") -> GT:
    """
    Create publication-quality scientific data table.
    """

*See sub-skills for full details.*

## Version History

- **1.0.0** (2026-01-17): Initial release
  - Basic table creation and styling
  - Column formatting (currency, percent, date)
  - Conditional formatting and color scales
  - Row and column grouping
  - Footnotes and annotations
  - Export to HTML and images
  - Complete report examples
  - Integration with Streamlit and Polars
  - Best practices and troubleshooting

## Resources

- **Official Documentation**: https://posit-dev.github.io/great-tables/
- **GitHub**: https://github.com/posit-dev/great-tables
- **PyPI**: https://pypi.org/project/great-tables/
- **Gallery**: https://posit-dev.github.io/great-tables/examples/

---

**Create publication-quality tables with Great Tables - beautiful data presentation made easy!**

## Sub-Skills

- [1. Basic Table Creation](1-basic-table-creation/SKILL.md)
- [2. Column Formatting](2-column-formatting/SKILL.md)
- [3. Styling and Colors](3-styling-and-colors/SKILL.md)
- [4. Conditional Formatting](4-conditional-formatting/SKILL.md)
- [5. Grouped Rows and Columns](5-grouped-rows-and-columns/SKILL.md)
- [6. Footnotes and Annotations (+1)](6-footnotes-and-annotations/SKILL.md)
- [Great Tables with Streamlit (+1)](great-tables-with-streamlit/SKILL.md)
- [1. Keep Tables Focused (+3)](1-keep-tables-focused/SKILL.md)
- [Common Issues](common-issues/SKILL.md)
