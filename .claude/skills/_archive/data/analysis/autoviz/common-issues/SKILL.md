---
name: autoviz-common-issues
description: 'Sub-skill of autoviz: Common Issues.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: Charts not displaying in Jupyter**
```python
# Solution: Use server format
%matplotlib inline
AV.AutoViz(filename="", dfte=df, chart_format="server")
```

**Issue: Memory error with large dataset**
```python
# Solution: Reduce sample size
AV.AutoViz(
    filename="",
    dfte=df,
    max_rows_analyzed=25000,  # Reduce sample
    max_cols_analyzed=15      # Limit columns
)
```

**Issue: Too many charts generated**
```python
# Solution: Limit columns analyzed
df_subset = df[["col1", "col2", "col3", "target"]]
AV.AutoViz(filename="", dfte=df_subset)
```

**Issue: Categorical columns not recognized**
```python
# Solution: Convert to proper dtype
df["category"] = df["category"].astype("category")
AV.AutoViz(filename="", dfte=df)
```

**Issue: Date columns causing issues**
```python
# Solution: Convert to datetime or extract features
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df_features = df.drop(columns=["date"])
AV.AutoViz(filename="", dfte=df_features)
```
