---
name: great-tables-4-conditional-formatting
description: 'Sub-skill of great-tables: 4. Conditional Formatting.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 4. Conditional Formatting

## 4. Conditional Formatting


**Color Scales:**
```python
from great_tables import GT
from great_tables import style, loc
from great_tables.data import countrypops
import pandas as pd

# Sample heatmap data
df = pd.DataFrame({
    "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "North": [85, 92, 88, 95, 91, 97],
    "South": [72, 78, 81, 75, 82, 88],
    "East": [90, 85, 92, 89, 94, 91],
    "West": [68, 75, 79, 82, 78, 85]
})

table = (
    GT(df)
    .tab_header(title="Regional Performance Scores")

    # Apply color scale to data columns
    .data_color(
        columns=["North", "South", "East", "West"],
        palette=["#FF6B6B", "#FFEB3B", "#4CAF50"],  # Red -> Yellow -> Green
        domain=[60, 100]
    )
)

table.save("color_scale.html")
```

**Conditional Icons:**
```python
from great_tables import GT, html
import pandas as pd

df = pd.DataFrame({
    "Metric": ["Revenue", "Users", "Conversion", "NPS"],
    "Current": [1250000, 85000, 3.2, 72],
    "Previous": [1180000, 78000, 3.5, 68],
    "Change_Pct": [5.9, 9.0, -8.6, 5.9]
})

def trend_icon(value):
    """Return trend icon based on value."""
    if value > 0:
        return html('<span style="color: green;">&#9650;</span>')  # Up arrow
    elif value < 0:
        return html('<span style="color: red;">&#9660;</span>')    # Down arrow
    else:
        return html('<span style="color: gray;">&#9654;</span>')   # Right arrow

# Add trend column
df["Trend"] = df["Change_Pct"].apply(trend_icon)

table = (
    GT(df)
    .tab_header(title="Key Metrics Dashboard")

    .fmt_number(columns="Current", use_seps=True, decimals=0)
    .fmt_number(columns="Previous", use_seps=True, decimals=0)
    .fmt_percent(columns="Change_Pct", decimals=1, scale_values=False)
)

table.save("conditional_icons.html")
```

**Bar Charts in Cells:**
```python
from great_tables import GT, html
import pandas as pd

df = pd.DataFrame({
    "Product": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"],
    "Sales": [85000, 120000, 65000, 95000, 110000],
    "Target": [100000, 100000, 100000, 100000, 100000]
})

def create_bar(value, max_value=150000):
    """Create inline bar chart."""
    width = min(value / max_value * 100, 100)
    color = "#4CAF50" if value >= 100000 else "#FF9800"
    return html(f'''
        <div style="background: #eee; width: 100px; height: 20px;">
            <div style="background: {color}; width: {width}%; height: 100%;"></div>
        </div>
    ''')

df["Progress"] = df["Sales"].apply(create_bar)

table = (
    GT(df)
    .tab_header(title="Sales Progress by Product")
    .fmt_number(columns="Sales", use_seps=True, decimals=0)
    .fmt_number(columns="Target", use_seps=True, decimals=0)
)

table.save("bar_charts.html")
```
