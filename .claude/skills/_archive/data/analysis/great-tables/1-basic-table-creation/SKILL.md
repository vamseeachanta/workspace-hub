---
name: great-tables-1-basic-table-creation
description: 'Sub-skill of great-tables: 1. Basic Table Creation.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. Basic Table Creation

## 1. Basic Table Creation


**Simplest Usage:**
```python
from great_tables import GT
import pandas as pd

# Create sample data
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "Diana"],
    "Department": ["Engineering", "Marketing", "Engineering", "Sales"],
    "Salary": [95000, 78000, 88000, 92000],
    "Years": [5, 3, 4, 6]
})

# Create basic table
table = GT(df)

# Display (in Jupyter) or save
table.save("basic_table.html")
```

**With Title and Subtitle:**
```python
from great_tables import GT, md
import pandas as pd

df = pd.DataFrame({
    "Product": ["Widget A", "Widget B", "Gadget X", "Gadget Y"],
    "Revenue": [150000, 220000, 180000, 95000],
    "Units": [1500, 2200, 900, 950],
    "Growth": [0.12, 0.25, 0.08, -0.05]
})

table = (
    GT(df)
    .tab_header(
        title="Q4 2025 Sales Performance",
        subtitle="Product line revenue and growth metrics"
    )
)

table.save("sales_table.html")
```

**With Source Notes:**
```python
from great_tables import GT
import pandas as pd

df = pd.DataFrame({
    "Country": ["USA", "UK", "Germany", "Japan"],
    "GDP_Trillion": [25.5, 3.1, 4.2, 4.9],
    "Population_Million": [331, 67, 83, 125]
})

table = (
    GT(df)
    .tab_header(
        title="World Economic Indicators",
        subtitle="Top economies by GDP"
    )
    .tab_source_note(
        source_note="Source: World Bank, 2024"
    )
    .tab_source_note(
        source_note="GDP in trillion USD"
    )
)

table.save("economy_table.html")
```
