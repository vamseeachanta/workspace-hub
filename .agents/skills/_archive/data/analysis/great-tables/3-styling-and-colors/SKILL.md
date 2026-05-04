---
name: great-tables-3-styling-and-colors
description: 'Sub-skill of great-tables: 3. Styling and Colors.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 3. Styling and Colors

## 3. Styling and Colors


**Background Colors:**
```python
from great_tables import GT
from great_tables import style, loc
import pandas as pd

df = pd.DataFrame({
    "Category": ["Electronics", "Clothing", "Food", "Home"],
    "Q1": [150000, 95000, 120000, 85000],
    "Q2": [180000, 88000, 135000, 92000],
    "Q3": [165000, 102000, 128000, 78000],
    "Q4": [210000, 115000, 145000, 105000]
})

table = (
    GT(df)
    .tab_header(title="Quarterly Sales by Category")

    # Style header row
    .tab_style(
        style=style.fill(color="#4a86e8"),
        locations=loc.column_labels()
    )
    .tab_style(
        style=style.text(color="white", weight="bold"),
        locations=loc.column_labels()
    )

    # Alternate row colors
    .tab_style(
        style=style.fill(color="#f3f3f3"),
        locations=loc.body(rows=[1, 3])  # Even rows
    )

    # Highlight specific cell
    .tab_style(
        style=style.fill(color="#90EE90"),
        locations=loc.body(columns="Q4", rows=[0])  # Highest Q4
    )
)

table.save("styled_table.html")
```

**Text Styling:**
```python
from great_tables import GT
from great_tables import style, loc
import pandas as pd

df = pd.DataFrame({
    "Rank": [1, 2, 3, 4, 5],
    "Company": ["TechCorp", "DataInc", "CloudSoft", "AILabs", "DevHub"],
    "Revenue_B": [125.4, 98.2, 87.5, 76.3, 65.8],
    "Change": [0.15, 0.08, -0.03, 0.22, -0.12]
})

table = (
    GT(df)
    .tab_header(title="Top Companies by Revenue")

    # Bold first column
    .tab_style(
        style=style.text(weight="bold"),
        locations=loc.body(columns="Rank")
    )

    # Italic company names
    .tab_style(
        style=style.text(style="italic"),
        locations=loc.body(columns="Company")
    )

    # Color positive/negative changes
    .tab_style(
        style=style.text(color="green"),
        locations=loc.body(columns="Change", rows=[0, 1, 3])  # Positive
    )
    .tab_style(
        style=style.text(color="red"),
        locations=loc.body(columns="Change", rows=[2, 4])  # Negative
    )

    # Format numbers
    .fmt_currency(columns="Revenue_B", currency="USD", decimals=1)
    .fmt_percent(columns="Change", decimals=1)
)

table.save("text_styled.html")
```

**Borders and Spacing:**
```python
from great_tables import GT
from great_tables import style, loc
import pandas as pd

df = pd.DataFrame({
    "Section": ["Introduction", "Methods", "Results", "Discussion"],
    "Pages": [5, 12, 18, 8],
    "Figures": [2, 6, 15, 3],
    "Tables": [0, 3, 8, 1]
})

table = (
    GT(df)
    .tab_header(title="Manuscript Structure")

    # Add border below header
    .tab_style(
        style=style.borders(sides="bottom", color="black", weight="2px"),
        locations=loc.column_labels()
    )

    # Add border below last row
    .tab_style(
        style=style.borders(sides="bottom", color="black", weight="2px"),
        locations=loc.body(rows=[-1])
    )

    # Cell padding
    .tab_options(
        data_row_padding="10px",
        column_labels_padding="12px"
    )
)

table.save("bordered_table.html")
```
