---
name: polars-3-expression-api
description: 'Sub-skill of polars: 3. Expression API.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 3. Expression API

## 3. Expression API


**Basic Expressions:**
```python
import polars as pl

df = pl.DataFrame({
    "a": [1, 2, 3, 4, 5],
    "b": [10, 20, 30, 40, 50],
    "c": ["x", "y", "x", "y", "x"],
    "d": [1.5, 2.5, 3.5, 4.5, 5.5]
})

# Column selection
df.select(pl.col("a"))
df.select(pl.col("a", "b", "c"))
df.select(pl.col("^a.*$"))  # Regex pattern
df.select(pl.all())
df.select(pl.exclude("c"))

# Arithmetic operations
df.select([
    pl.col("a"),
    (pl.col("a") + pl.col("b")).alias("sum"),
    (pl.col("a") * pl.col("d")).alias("product"),
    (pl.col("b") / pl.col("a")).alias("ratio"),
    (pl.col("a") ** 2).alias("squared"),
    (pl.col("a") % 2).alias("modulo")
])

# Conditional expressions
df.select([
    pl.col("a"),
    pl.when(pl.col("a") > 3)
      .then(pl.lit("high"))
      .otherwise(pl.lit("low"))
      .alias("category"),

    pl.when(pl.col("a") < 2)
      .then(pl.lit("low"))
      .when(pl.col("a") < 4)
      .then(pl.lit("medium"))
      .otherwise(pl.lit("high"))
      .alias("tier")
])

# String operations
df_str = pl.DataFrame({
    "text": ["Hello World", "Polars is Fast", "Data Analysis"]
})

df_str.select([
    pl.col("text"),
    pl.col("text").str.to_lowercase().alias("lower"),
    pl.col("text").str.to_uppercase().alias("upper"),
    pl.col("text").str.len_chars().alias("length"),
    pl.col("text").str.split(" ").alias("words"),
    pl.col("text").str.contains("a").alias("has_a"),
    pl.col("text").str.replace("a", "X").alias("replaced")
])
```

**Advanced Expressions:**
```python
# List operations
df_list = pl.DataFrame({
    "values": [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
})

df_list.select([
    pl.col("values"),
    pl.col("values").list.len().alias("count"),
    pl.col("values").list.sum().alias("sum"),
    pl.col("values").list.mean().alias("mean"),
    pl.col("values").list.first().alias("first"),
    pl.col("values").list.last().alias("last"),
    pl.col("values").list.get(0).alias("index_0"),
    pl.col("values").list.contains(5).alias("has_5")
])

# Struct operations
df_struct = pl.DataFrame({
    "point": [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
})

df_struct.select([
    pl.col("point"),
    pl.col("point").struct.field("x").alias("x"),
    pl.col("point").struct.field("y").alias("y")
])

# Date/time operations
df_dt = pl.DataFrame({
    "timestamp": pl.date_range(
        datetime(2025, 1, 1),
        datetime(2025, 12, 31),
        "1d",
        eager=True
    )
})

df_dt.select([
    pl.col("timestamp"),
    pl.col("timestamp").dt.year().alias("year"),
    pl.col("timestamp").dt.month().alias("month"),
    pl.col("timestamp").dt.day().alias("day"),
    pl.col("timestamp").dt.weekday().alias("weekday"),
    pl.col("timestamp").dt.week().alias("week"),
    pl.col("timestamp").dt.quarter().alias("quarter"),
    pl.col("timestamp").dt.strftime("%Y-%m-%d").alias("formatted")
])
```
