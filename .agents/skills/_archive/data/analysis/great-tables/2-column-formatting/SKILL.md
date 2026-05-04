---
name: great-tables-2-column-formatting
description: 'Sub-skill of great-tables: 2. Column Formatting.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 2. Column Formatting

## 2. Column Formatting


**Numeric Formatting:**
```python
from great_tables import GT
import pandas as pd

df = pd.DataFrame({
    "Item": ["Product A", "Product B", "Product C"],
    "Price": [29.99, 149.50, 9.99],
    "Revenue": [1500000, 2250000, 890000],
    "Margin": [0.35, 0.42, 0.28],
    "Units": [50000, 15000, 89000]
})

table = (
    GT(df)
    .tab_header(title="Product Metrics")

    # Format as currency
    .fmt_currency(
        columns="Price",
        currency="USD"
    )

    # Format large numbers with suffixes
    .fmt_number(
        columns="Revenue",
        use_seps=True,
        decimals=0
    )

    # Format as percentage
    .fmt_percent(
        columns="Margin",
        decimals=1
    )

    # Format with thousand separators
    .fmt_integer(
        columns="Units",
        use_seps=True
    )
)

table.save("numeric_formatting.html")
```

**Date and Time Formatting:**
```python
from great_tables import GT
import pandas as pd
from datetime import datetime, date

df = pd.DataFrame({
    "Event": ["Launch", "Update", "Maintenance", "Release"],
    "Date": [
        date(2025, 1, 15),
        date(2025, 3, 22),
        date(2025, 6, 1),
        date(2025, 9, 30)
    ],
    "Timestamp": [
        datetime(2025, 1, 15, 9, 0),
        datetime(2025, 3, 22, 14, 30),
        datetime(2025, 6, 1, 2, 0),
        datetime(2025, 9, 30, 10, 0)
    ]
})

table = (
    GT(df)
    .tab_header(title="Product Timeline")

    # Format date
    .fmt_date(
        columns="Date",
        date_style="day_month_year"
    )

    # Format datetime
    .fmt_datetime(
        columns="Timestamp",
        date_style="yMd",
        time_style="Hm"
    )
)

table.save("date_formatting.html")
```

**Custom Number Formatting:**
```python
from great_tables import GT
import pandas as pd

df = pd.DataFrame({
    "Metric": ["Users", "Revenue", "Conversion", "Avg Order"],
    "Value": [1234567, 5678901.23, 0.0342, 156.789]
})

table = (
    GT(df)
    .tab_header(title="Dashboard Metrics")

    # Custom suffixes for large numbers
    .fmt_number(
        columns="Value",
        rows=[0],  # First row only
        compact=True  # Use K, M, B suffixes
    )

    # Currency for second row
    .fmt_currency(
        columns="Value",
        rows=[1],
        currency="USD",
        decimals=0
    )

    # Percentage for third row
    .fmt_percent(
        columns="Value",
        rows=[2],
        decimals=2
    )

    # Standard number for fourth row
    .fmt_currency(
        columns="Value",
        rows=[3],
        currency="USD",
        decimals=2
    )
)

table.save("custom_formatting.html")
```
