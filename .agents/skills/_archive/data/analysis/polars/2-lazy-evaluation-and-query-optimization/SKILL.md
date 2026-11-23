---
name: polars-2-lazy-evaluation-and-query-optimization
description: 'Sub-skill of polars: 2. Lazy Evaluation and Query Optimization.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 2. Lazy Evaluation and Query Optimization

## 2. Lazy Evaluation and Query Optimization


**LazyFrame Basics:**
```python
import polars as pl

# Create lazy frame (no computation yet)
lf = pl.scan_csv("large_data.csv")

# Or convert from eager DataFrame
df = pl.DataFrame({"x": [1, 2, 3]})
lf = df.lazy()

# Chain operations (still no computation)
result_lf = (
    lf
    .filter(pl.col("date") >= "2025-01-01")
    .with_columns([
        (pl.col("revenue") - pl.col("cost")).alias("profit"),
        pl.col("category").cast(pl.Categorical)
    ])
    .group_by("category")
    .agg([
        pl.col("profit").sum().alias("total_profit"),
        pl.col("profit").mean().alias("avg_profit"),
        pl.count().alias("count")
    ])
    .sort("total_profit", descending=True)
)

# View the query plan
print(result_lf.explain())

# Execute and collect results
result_df = result_lf.collect()

# Execute with streaming (for very large data)
result_df = result_lf.collect(streaming=True)

# Fetch only first N rows
sample = result_lf.fetch(1000)
```

**Query Optimization Benefits:**
```python
# Polars optimizes this automatically:
lf = (
    pl.scan_parquet("data/*.parquet")
    .filter(pl.col("country") == "USA")  # Predicate pushdown
    .select(["id", "name", "revenue"])   # Projection pushdown
    .filter(pl.col("revenue") > 1000)    # Combined with first filter
)

# View optimized plan
print("Naive plan:")
print(lf.explain(optimized=False))

print("\nOptimized plan:")
print(lf.explain(optimized=True))

# The optimizer will:
# 1. Push filters to data source (read less data)
# 2. Select only needed columns (reduce memory)
# 3. Combine/reorder operations for efficiency
# 4. Eliminate redundant operations
```

**Streaming Large Files:**
```python
# Process files larger than memory
def process_large_file(input_path: str, output_path: str):
    """Process file that doesn't fit in memory."""
    result = (
        pl.scan_csv(input_path)
        .filter(pl.col("status") == "active")
        .group_by("region")
        .agg([
            pl.col("sales").sum(),
            pl.col("customers").n_unique()
        ])
        .collect(streaming=True)  # Stream processing
    )

    result.write_parquet(output_path)
    return result

# Sink directly to file (even more memory efficient)
(
    pl.scan_csv("huge_file.csv")
    .filter(pl.col("value") > 0)
    .sink_parquet("filtered_output.parquet")
)
```
