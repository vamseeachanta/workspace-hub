---
name: polars-6-joins-and-concatenation
description: 'Sub-skill of polars: 6. Joins and Concatenation.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 6. Joins and Concatenation

## 6. Joins and Concatenation


**Join Operations:**
```python
import polars as pl

# Sample data
orders = pl.DataFrame({
    "order_id": [1, 2, 3, 4, 5],
    "customer_id": [101, 102, 101, 103, 104],
    "amount": [250.0, 150.0, 300.0, 200.0, 175.0]
})

customers = pl.DataFrame({
    "customer_id": [101, 102, 103, 105],
    "name": ["Alice", "Bob", "Charlie", "Diana"],
    "region": ["East", "West", "East", "North"]
})

# Inner join (default)
result = orders.join(customers, on="customer_id", how="inner")

# Left join
result = orders.join(customers, on="customer_id", how="left")

# Right join
result = orders.join(customers, on="customer_id", how="right")

# Outer/full join
result = orders.join(customers, on="customer_id", how="full")

# Cross join (cartesian product)
result = orders.join(customers, how="cross")

# Semi join (filter left by right)
result = orders.join(customers, on="customer_id", how="semi")

# Anti join (filter left NOT in right)
result = orders.join(customers, on="customer_id", how="anti")

# Join on multiple columns
df1 = pl.DataFrame({"a": [1, 2], "b": ["x", "y"], "val1": [10, 20]})
df2 = pl.DataFrame({"a": [1, 2], "b": ["x", "z"], "val2": [100, 200]})
result = df1.join(df2, on=["a", "b"], how="inner")

# Join with different column names
result = orders.join(
    customers.rename({"customer_id": "cust_id"}),
    left_on="customer_id",
    right_on="cust_id"
)

# Join with suffix for duplicate columns
df1 = pl.DataFrame({"id": [1, 2], "value": [10, 20]})
df2 = pl.DataFrame({"id": [1, 2], "value": [100, 200]})
result = df1.join(df2, on="id", suffix="_right")
```

**Concatenation:**
```python
# Vertical concatenation (stack rows)
df1 = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
df2 = pl.DataFrame({"a": [5, 6], "b": [7, 8]})
df3 = pl.DataFrame({"a": [9, 10], "b": [11, 12]})

combined = pl.concat([df1, df2, df3])

# Horizontal concatenation (stack columns)
df1 = pl.DataFrame({"a": [1, 2, 3]})
df2 = pl.DataFrame({"b": [4, 5, 6]})
combined = pl.concat([df1, df2], how="horizontal")

# Diagonal concatenation (union with different schemas)
df1 = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
df2 = pl.DataFrame({"b": [5, 6], "c": [7, 8]})
combined = pl.concat([df1, df2], how="diagonal")

# Align schemas before concat
df1 = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
df2 = pl.DataFrame({"a": [5, 6], "c": [7, 8]})
combined = pl.concat([df1, df2], how="diagonal_relaxed")
```

**Asof Joins (Time-based):**
```python
# For joining on nearest timestamp
trades = pl.DataFrame({
    "time": pl.datetime_range(datetime(2025, 1, 1, 9, 0), datetime(2025, 1, 1, 9, 10), "1m", eager=True),
    "price": [100.0, 101.0, 100.5, 102.0, 101.5, 103.0, 102.5, 104.0, 103.5, 105.0, 104.5]
})

quotes = pl.DataFrame({
    "time": pl.datetime_range(datetime(2025, 1, 1, 9, 0), datetime(2025, 1, 1, 9, 10), "2m", eager=True),
    "bid": [99.5, 100.5, 101.5, 102.5, 103.5, 104.5]
})

# Join each trade with the most recent quote
result = trades.join_asof(
    quotes,
    on="time",
    strategy="backward"  # Use most recent quote
)
```
