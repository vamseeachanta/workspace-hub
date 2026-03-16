---
name: great-tables-6-footnotes-and-annotations
description: 'Sub-skill of great-tables: 6. Footnotes and Annotations (+1).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 6. Footnotes and Annotations (+1)

## 6. Footnotes and Annotations


**Adding Footnotes:**
```python
from great_tables import GT
from great_tables import loc
import pandas as pd

df = pd.DataFrame({
    "Company": ["TechCorp", "DataInc", "CloudSoft", "AILabs"],
    "Revenue_B": [125.4, 98.2, 87.5, 76.3],
    "Employees": [45000, 28000, 15000, 8500],
    "Founded": [1985, 1998, 2010, 2015]
})

table = (
    GT(df)
    .tab_header(
        title="Tech Companies Overview",
        subtitle="Leading technology firms"
    )

    # Add footnote to title
    .tab_footnote(
        footnote="Revenue in billions USD",
        locations=loc.title()
    )

    # Add footnote to specific column
    .tab_footnote(
        footnote="Full-time employees only",
        locations=loc.column_labels(columns="Employees")
    )

    # Add footnote to specific cell
    .tab_footnote(
        footnote="Acquired by MegaCorp in 2024",
        locations=loc.body(columns="Company", rows=[2])
    )

    # Source note
    .tab_source_note(
        source_note="Data as of December 2025"
    )

    .fmt_currency(columns="Revenue_B", currency="USD", decimals=1)
    .fmt_integer(columns="Employees", use_seps=True)
)

table.save("footnotes.html")
```

**Stubhead Labels:**
```python
from great_tables import GT
import pandas as pd

df = pd.DataFrame({
    "Year": [2022, 2023, 2024, 2025],
    "Revenue": [85.2, 92.5, 105.8, 118.3],
    "Profit": [12.5, 15.8, 19.2, 23.1],
    "Margin": [0.147, 0.171, 0.181, 0.195]
})

table = (
    GT(df, rowname_col="Year")
    .tab_header(title="Financial Summary")
    .tab_stubhead(label="Fiscal Year")  # Label for row names column

    .fmt_currency(columns=["Revenue", "Profit"], currency="USD", decimals=1)
    .fmt_percent(columns="Margin", decimals=1)
)

table.save("stubhead.html")
```


## 7. Export Options


**Export to HTML:**
```python
from great_tables import GT
import pandas as pd

df = pd.DataFrame({
    "Item": ["A", "B", "C"],
    "Value": [100, 200, 150]
})

table = GT(df).tab_header(title="Export Demo")

# Save as HTML file
table.save("table.html")

# Get HTML string
html_string = table.as_raw_html()
print(html_string[:500])  # Preview
```

**Export to Image (PNG):**
```python
from great_tables import GT
import pandas as pd

df = pd.DataFrame({
    "Product": ["Widget", "Gadget", "Tool"],
    "Price": [29.99, 49.99, 19.99],
    "Stock": [150, 85, 200]
})

table = (
    GT(df)
    .tab_header(title="Product Inventory")
    .fmt_currency(columns="Price", currency="USD")
)

# Save as PNG (requires webshot/chromedriver)
# table.save("table.png")

# Alternative: Use playwright
# table.save("table.png", web_driver="playwright")
```

**Inline Display in Notebooks:**
```python
from great_tables import GT
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Score": [95, 87, 92]
})

# In Jupyter, just return the table object
table = GT(df).tab_header(title="Test Scores")
table  # Displays inline
```
