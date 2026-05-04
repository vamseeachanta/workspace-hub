---
name: great-tables-great-tables-with-streamlit
description: 'Sub-skill of great-tables: Great Tables with Streamlit (+1).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# Great Tables with Streamlit (+1)

## Great Tables with Streamlit


```python
import streamlit as st
from great_tables import GT
import pandas as pd

st.set_page_config(page_title="Table Demo", layout="wide")
st.title("Great Tables in Streamlit")

# Sample data
df = pd.DataFrame({
    "Product": ["Widget A", "Widget B", "Gadget X"],
    "Price": [29.99, 49.99, 19.99],
    "Stock": [150, 85, 200],
    "Rating": [4.5, 4.2, 4.8]
})

# Create table
table = (
    GT(df)
    .tab_header(title="Product Catalog")
    .fmt_currency(columns="Price", currency="USD")
    .fmt_number(columns="Rating", decimals=1)
)

# Display in Streamlit
st.html(table.as_raw_html())
```


## Great Tables with Polars


```python
from great_tables import GT
import polars as pl

# Create Polars DataFrame
df_polars = pl.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "score": [95, 87, 92],
    "grade": ["A", "B+", "A-"]
})

# Convert to pandas for Great Tables
df_pandas = df_polars.to_pandas()

# Create table
table = (
    GT(df_pandas)
    .tab_header(title="Student Scores")
    .cols_label(
        name="Student",
        score="Score",
        grade="Grade"
    )
)

table.save("polars_table.html")
```
