---
name: polars-1-use-lazy-evaluation-by-default
description: 'Sub-skill of polars: 1. Use Lazy Evaluation by Default (+4).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. Use Lazy Evaluation by Default (+4)

## 1. Use Lazy Evaluation by Default


```python
# GOOD: Lazy evaluation allows optimization
lf = pl.scan_parquet("data.parquet")
result = (
    lf
    .filter(pl.col("x") > 0)
    .select(["x", "y"])
    .collect()
)

# AVOID: Eager evaluation for large files
df = pl.read_parquet("data.parquet")  # Loads everything
df = df.filter(pl.col("x") > 0)
df = df.select(["x", "y"])
```


## 2. Chain Operations


```python
# GOOD: Single chain, optimized execution
result = (
    df
    .filter(pl.col("status") == "active")
    .with_columns([
        (pl.col("a") + pl.col("b")).alias("sum"),
        pl.col("date").dt.year().alias("year")
    ])
    .group_by("year")
    .agg(pl.col("sum").mean())
)

# AVOID: Multiple separate operations
df = df.filter(pl.col("status") == "active")
df = df.with_columns((pl.col("a") + pl.col("b")).alias("sum"))
df = df.with_columns(pl.col("date").dt.year().alias("year"))
result = df.group_by("year").agg(pl.col("sum").mean())
```


## 3. Use Appropriate Data Types


```python
# Optimize memory with correct types
df = df.with_columns([
    pl.col("small_int").cast(pl.Int16),
    pl.col("category").cast(pl.Categorical),
    pl.col("flag").cast(pl.Boolean),
    pl.col("precise_float").cast(pl.Float32)  # If precision allows
])

# Check memory usage
print(df.estimated_size("mb"))
```


## 4. Filter Early


```python
# GOOD: Filter before expensive operations
result = (
    pl.scan_parquet("data.parquet")
    .filter(pl.col("date") >= "2025-01-01")  # Filter first
    .group_by("category")
    .agg(pl.col("value").sum())
    .collect()
)

# AVOID: Filter after loading everything
result = (
    pl.scan_parquet("data.parquet")
    .group_by("category")
    .agg(pl.col("value").sum())
    .filter(...)  # Too late, already processed all data
    .collect()
)
```


## 5. Use Expressions Over Apply


```python
# GOOD: Vectorized expression
df.with_columns([
    pl.when(pl.col("x") > 0).then(pl.col("x")).otherwise(0).alias("positive_x")
])

# AVOID: Python function (slow)
df.with_columns([
    pl.col("x").map_elements(lambda v: v if v > 0 else 0).alias("positive_x")
])
```
