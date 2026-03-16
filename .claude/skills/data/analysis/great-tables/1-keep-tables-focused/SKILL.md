---
name: great-tables-1-keep-tables-focused
description: 'Sub-skill of great-tables: 1. Keep Tables Focused (+3).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. Keep Tables Focused (+3)

## 1. Keep Tables Focused


```python
# GOOD: Select relevant columns
df_display = df[["Name", "Revenue", "Growth"]]
table = GT(df_display)

# AVOID: Displaying too many columns
# table = GT(df)  # If df has 20+ columns
```


## 2. Use Appropriate Formatting


```python
# GOOD: Match format to data type
table = (
    GT(df)
    .fmt_currency(columns="Price", currency="USD")
    .fmt_percent(columns="Growth", decimals=1)
    .fmt_integer(columns="Units", use_seps=True)
)

# AVOID: Generic number format for everything
```


## 3. Limit Rows for Display


```python
# GOOD: Show summary or top N
df_top10 = df.nlargest(10, "Revenue")
table = GT(df_top10)

# AVOID: Displaying thousands of rows
```


## 4. Use Color Sparingly


```python
# GOOD: Highlight key information
table.data_color(
    columns="Performance",
    palette=["#fee2e2", "#dcfce7"],  # Subtle colors
    domain=[0, 100]
)

# AVOID: Rainbow color schemes
```
