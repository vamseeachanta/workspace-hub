---
name: ydata-profiling-common-issues
description: 'Sub-skill of ydata-profiling: Common Issues.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: Memory error with large dataset**
```python
# Solution 1: Use minimal mode
profile = ProfileReport(df, minimal=True)

# Solution 2: Sample data
profile = ProfileReport(df.sample(50000))
```

**Issue: Slow report generation**
```python
# Solution: Disable expensive computations
profile = ProfileReport(
    df,
    correlations=None,
    interactions={"continuous": False},
    missing_diagrams={"matrix": False, "heatmap": False}
)
```

**Issue: Report too large**
```python
# Solution: Limit samples shown
profile = ProfileReport(
    df,
    samples={"head": 5, "tail": 5},
    duplicates={"head": 5}
)
```

**Issue: DateTime not recognized**
```python
# Solution: Convert explicitly
df["date_col"] = pd.to_datetime(df["date_col"])
profile = ProfileReport(df)
```
