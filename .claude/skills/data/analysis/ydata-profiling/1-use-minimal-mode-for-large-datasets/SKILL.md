---
name: ydata-profiling-1-use-minimal-mode-for-large-datasets
description: 'Sub-skill of ydata-profiling: 1. Use Minimal Mode for Large Datasets
  (+3).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. Use Minimal Mode for Large Datasets (+3)

## 1. Use Minimal Mode for Large Datasets


```python
# GOOD: Minimal mode for large data
profile = ProfileReport(large_df, minimal=True)

# AVOID: Full explorative on large data
# profile = ProfileReport(large_df, explorative=True)  # Slow!
```


## 2. Sample for Initial Exploration


```python
# GOOD: Sample first, then full profile
sample = df.sample(n=10000, random_state=42)
profile = ProfileReport(sample, title="Sample Profile")

# If interesting, profile full data
# profile_full = ProfileReport(df, minimal=True)
```


## 3. Customize for Your Needs


```python
# GOOD: Disable unnecessary computations
profile = ProfileReport(
    df,
    correlations={"pearson": {"calculate": True}},  # Only Pearson
    missing_diagrams={"bar": True, "matrix": False, "heatmap": False}
)
```


## 4. Use Lazy Evaluation


```python
# GOOD: Lazy profile, compute when needed
profile = ProfileReport(df, lazy=True)
# ... do other work ...
profile.to_file("report.html")  # Computes here
```
