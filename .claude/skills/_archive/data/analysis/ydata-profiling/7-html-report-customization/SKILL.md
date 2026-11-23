---
name: ydata-profiling-7-html-report-customization
description: 'Sub-skill of ydata-profiling: 7. HTML Report Customization.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 7. HTML Report Customization

## 7. HTML Report Customization


**Custom Report Configuration:**
```python
from ydata_profiling import ProfileReport
import pandas as pd

df = pd.read_csv("data.csv")

# Customized report
profile = ProfileReport(
    df,
    title="Custom Styled Report",
    dataset={
        "description": "This is a sample dataset for analysis",
        "creator": "Data Team",
        "copyright_holder": "Company Inc.",
        "copyright_year": "2025",
        "url": "https://company.com/data"
    },
    variables={
        "descriptions": {
            "revenue": "Total revenue in USD",
            "units": "Number of units sold",
            "category": "Product category"
        }
    },
    html={
        "style": {
            "full_width": True
        },
        "navbar_show": True,
        "minify_html": True
    },
    progress_bar=True
)

profile.to_file("custom_report.html")
```

**Report Sections Control:**
```python
from ydata_profiling import ProfileReport
import pandas as pd

df = pd.read_csv("data.csv")

# Control which sections appear
profile = ProfileReport(
    df,
    title="Selective Report",
    samples={
        "head": 10,  # Show first 10 rows
        "tail": 10   # Show last 10 rows
    },
    duplicates={
        "head": 10  # Show first 10 duplicate rows
    },
    correlations={
        "pearson": {"calculate": True},
        "spearman": {"calculate": False},  # Skip Spearman
        "kendall": {"calculate": False},   # Skip Kendall
        "phi_k": {"calculate": False}      # Skip Phi-K
    },
    missing_diagrams={
        "bar": True,
        "matrix": False,  # Skip matrix
        "heatmap": False  # Skip heatmap
    }
)

profile.to_file("selective_report.html")
```

**Export Options:**
```python
from ydata_profiling import ProfileReport
import pandas as pd
import json

df = pd.read_csv("data.csv")
profile = ProfileReport(df, title="Export Demo")

# Export to HTML
profile.to_file("report.html")

# Export to JSON
profile.to_file("report.json")

# Get JSON as string
json_output = profile.to_json()

# Get as dictionary
description_dict = profile.get_description()

# Save widgets for notebook
profile.to_widgets()
```
