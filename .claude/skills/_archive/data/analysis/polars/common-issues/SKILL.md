---
name: polars-common-issues
description: 'Sub-skill of polars: Common Issues.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: Out of Memory**
```python
# Solution 1: Use streaming
result = lf.collect(streaming=True)

# Solution 2: Sink to file
lf.sink_parquet("output.parquet")

# Solution 3: Process in chunks
for chunk in pl.read_csv_batched("large.csv", batch_size=100000):
    process(chunk)
```

**Issue: Slow Performance**
```python
# Check query plan for inefficiencies
print(lf.explain(optimized=True))

# Use profiling
result = lf.profile()
print(result[1])  # Timing information
```

**Issue: Type Mismatch in Join**
```python
# Ensure matching types before join
df1 = df1.with_columns(pl.col("id").cast(pl.Int64))
df2 = df2.with_columns(pl.col("id").cast(pl.Int64))
result = df1.join(df2, on="id")
```

**Issue: Date Parsing Errors**
```python
# Explicit format specification
df = df.with_columns([
    pl.col("date_str").str.strptime(pl.Date, "%Y-%m-%d"),
    pl.col("datetime_str").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S")
])
```
