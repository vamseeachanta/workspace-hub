---
name: polars-4-groupby-and-aggregations
description: 'Sub-skill of polars: 4. GroupBy and Aggregations (+1).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 4. GroupBy and Aggregations (+1)

## 4. GroupBy and Aggregations


**Basic GroupBy:**
```python
import polars as pl

df = pl.DataFrame({
    "category": ["A", "B", "A", "B", "A", "C"],
    "subcategory": ["x", "y", "x", "y", "z", "x"],
    "value": [100, 200, 150, 250, 175, 300],
    "quantity": [10, 20, 15, 25, 12, 30]
})

# Simple aggregation
result = df.group_by("category").agg([
    pl.col("value").sum().alias("total_value"),
    pl.col("value").mean().alias("avg_value"),
    pl.col("value").min().alias("min_value"),
    pl.col("value").max().alias("max_value"),
    pl.col("value").std().alias("std_value"),
    pl.col("quantity").sum().alias("total_quantity"),
    pl.count().alias("count")
])

print(result)

# Multiple group keys
result = df.group_by(["category", "subcategory"]).agg([
    pl.col("value").sum(),
    pl.count()
])

# Maintain order
result = df.group_by("category", maintain_order=True).agg(
    pl.col("value").sum()
)

# Dynamic aggregations
agg_exprs = [
    pl.col(c).mean().alias(f"{c}_mean")
    for c in ["value", "quantity"]
]
result = df.group_by("category").agg(agg_exprs)
```

**Advanced Aggregations:**
```python
# Multiple aggregations on same column
result = df.group_by("category").agg([
    pl.col("value").sum().alias("sum"),
    pl.col("value").mean().alias("mean"),
    pl.col("value").median().alias("median"),
    pl.col("value").quantile(0.25).alias("q25"),
    pl.col("value").quantile(0.75).alias("q75"),
    pl.col("value").var().alias("variance"),
    pl.col("value").skew().alias("skewness")
])

# Conditional aggregations
result = df.group_by("category").agg([
    pl.col("value").filter(pl.col("quantity") > 15).sum().alias("high_qty_value"),
    pl.col("value").filter(pl.col("quantity") <= 15).sum().alias("low_qty_value")
])

# First/last values
result = df.group_by("category").agg([
    pl.col("value").first().alias("first_value"),
    pl.col("value").last().alias("last_value"),
    pl.col("value").head(3).alias("top_3"),
    pl.col("value").tail(2).alias("bottom_2")
])

# Unique values
result = df.group_by("category").agg([
    pl.col("subcategory").n_unique().alias("unique_subcats"),
    pl.col("subcategory").unique().alias("subcategories")
])

# Custom aggregation with map_elements
result = df.group_by("category").agg([
    pl.col("value").map_elements(
        lambda s: s.to_numpy().std(ddof=1),
        return_dtype=pl.Float64
    ).alias("custom_std")
])
```


## 5. Window Functions


**Basic Window Functions:**
```python
import polars as pl

df = pl.DataFrame({
    "date": pl.date_range(date(2025, 1, 1), date(2025, 1, 10), eager=True),
    "category": ["A", "B"] * 5,
    "value": [100, 110, 105, 115, 108, 120, 112, 125, 118, 130]
})

# Row number within groups
df.with_columns([
    pl.col("value").rank().over("category").alias("rank"),
    pl.col("value").rank(descending=True).over("category").alias("rank_desc")
])

# Running calculations
df.with_columns([
    pl.col("value").cum_sum().over("category").alias("cumsum"),
    pl.col("value").cum_max().over("category").alias("cummax"),
    pl.col("value").cum_min().over("category").alias("cummin"),
    pl.col("value").cum_count().over("category").alias("cumcount")
])

# Lag and lead
df.with_columns([
    pl.col("value").shift(1).over("category").alias("lag_1"),
    pl.col("value").shift(-1).over("category").alias("lead_1"),
    pl.col("value").shift(2).over("category").alias("lag_2"),
    (pl.col("value") - pl.col("value").shift(1).over("category")).alias("diff")
])

# Percentage change
df.with_columns([
    pl.col("value").pct_change().over("category").alias("pct_change")
])
```

**Rolling Windows:**
```python
# Rolling calculations
df.with_columns([
    pl.col("value").rolling_mean(window_size=3).over("category").alias("rolling_mean_3"),
    pl.col("value").rolling_sum(window_size=3).over("category").alias("rolling_sum_3"),
    pl.col("value").rolling_std(window_size=3).over("category").alias("rolling_std_3"),
    pl.col("value").rolling_min(window_size=3).over("category").alias("rolling_min_3"),
    pl.col("value").rolling_max(window_size=3).over("category").alias("rolling_max_3")
])

# Time-based rolling windows
df_ts = pl.DataFrame({
    "timestamp": pl.datetime_range(
        datetime(2025, 1, 1),
        datetime(2025, 1, 10),
        "1h",
        eager=True
    ),
    "value": range(217)
})

df_ts.with_columns([
    pl.col("value").rolling_mean_by(
        by="timestamp",
        window_size="6h"
    ).alias("rolling_mean_6h"),

    pl.col("value").rolling_sum_by(
        by="timestamp",
        window_size="1d"
    ).alias("rolling_sum_1d")
])

# Exponential weighted functions
df.with_columns([
    pl.col("value").ewm_mean(span=3).alias("ewm_mean"),
    pl.col("value").ewm_std(span=3).alias("ewm_std")
])
```
