---
name: great-tables-5-grouped-rows-and-columns
description: 'Sub-skill of great-tables: 5. Grouped Rows and Columns.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 5. Grouped Rows and Columns

## 5. Grouped Rows and Columns


**Row Groups:**
```python
from great_tables import GT
import pandas as pd

df = pd.DataFrame({
    "Region": ["North", "North", "South", "South", "East", "East", "West", "West"],
    "Product": ["Widget", "Gadget", "Widget", "Gadget", "Widget", "Gadget", "Widget", "Gadget"],
    "Sales": [45000, 32000, 38000, 41000, 52000, 28000, 35000, 39000],
    "Units": [450, 160, 380, 205, 520, 140, 350, 195]
})

table = (
    GT(df, groupname_col="Region")  # Group by Region
    .tab_header(
        title="Sales by Region and Product",
        subtitle="Q4 2025 Performance"
    )
    .fmt_currency(columns="Sales", currency="USD", decimals=0)
    .fmt_integer(columns="Units", use_seps=True)

    # Style group labels
    .tab_style(
        style=[
            style.fill(color="#e8e8e8"),
            style.text(weight="bold")
        ],
        locations=loc.row_groups()
    )
)

table.save("row_groups.html")
```

**Column Spanners:**
```python
from great_tables import GT
import pandas as pd

df = pd.DataFrame({
    "Product": ["Widget A", "Widget B", "Gadget X"],
    "Q1_Sales": [25000, 32000, 18000],
    "Q1_Units": [250, 320, 90],
    "Q2_Sales": [28000, 35000, 22000],
    "Q2_Units": [280, 350, 110],
    "Q3_Sales": [31000, 38000, 25000],
    "Q3_Units": [310, 380, 125]
})

table = (
    GT(df)
    .tab_header(title="Quarterly Performance")

    # Create column spanners
    .tab_spanner(
        label="Q1",
        columns=["Q1_Sales", "Q1_Units"]
    )
    .tab_spanner(
        label="Q2",
        columns=["Q2_Sales", "Q2_Units"]
    )
    .tab_spanner(
        label="Q3",
        columns=["Q3_Sales", "Q3_Units"]
    )

    # Rename columns
    .cols_label(
        Q1_Sales="Sales",
        Q1_Units="Units",
        Q2_Sales="Sales",
        Q2_Units="Units",
        Q3_Sales="Sales",
        Q3_Units="Units"
    )

    # Format numbers
    .fmt_currency(columns=["Q1_Sales", "Q2_Sales", "Q3_Sales"], currency="USD", decimals=0)
    .fmt_integer(columns=["Q1_Units", "Q2_Units", "Q3_Units"], use_seps=True)
)

table.save("column_spanners.html")
```

**Nested Groups:**
```python
from great_tables import GT
import pandas as pd

df = pd.DataFrame({
    "Division": ["Consumer", "Consumer", "Consumer", "Enterprise", "Enterprise", "Enterprise"],
    "Category": ["Electronics", "Home", "Fashion", "Software", "Hardware", "Services"],
    "Product": ["Phones", "Furniture", "Apparel", "Cloud", "Servers", "Consulting"],
    "Revenue": [150, 45, 78, 220, 180, 95],
    "Growth": [0.12, 0.05, -0.02, 0.25, 0.08, 0.15]
})

table = (
    GT(df, groupname_col="Division", rowname_col="Category")
    .tab_header(
        title="Business Unit Performance",
        subtitle="Annual Revenue (Millions USD)"
    )
    .fmt_currency(columns="Revenue", currency="USD", decimals=0)
    .fmt_percent(columns="Growth", decimals=1)
)

table.save("nested_groups.html")
```
