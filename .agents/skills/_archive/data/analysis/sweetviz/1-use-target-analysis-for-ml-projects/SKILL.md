---
name: sweetviz-1-use-target-analysis-for-ml-projects
description: 'Sub-skill of sweetviz: 1. Use Target Analysis for ML Projects (+4).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. Use Target Analysis for ML Projects (+4)

## 1. Use Target Analysis for ML Projects


```python
# GOOD: Always specify target for ML datasets
report = sv.analyze(df, target_feat="target")

# AVOID: Missing target analysis
report = sv.analyze(df)  # No target relationship shown
```


## 2. Sample Large Datasets


```python
# GOOD: Sample for large datasets
if len(df) > 100000:
    df_sample = df.sample(n=100000, random_state=42)
    report = sv.analyze(df_sample)
else:
    report = sv.analyze(df)

# AVOID: Analyzing huge datasets directly
# report = sv.analyze(df_with_millions_of_rows)  # Very slow
```


## 3. Configure Feature Types Properly


```python
# GOOD: Force categorical for ID-like numeric columns
config = sv.FeatureConfig(
    skip=["customer_id", "transaction_id"],
    force_cat=["zip_code", "area_code", "rating"]
)
report = sv.analyze(df, feat_cfg=config)

# AVOID: Letting Sweetviz treat zip codes as numeric
```


## 4. Use Comparison for Validation


```python
# GOOD: Compare train/test for data leakage detection
comparison = sv.compare(
    [train_df, "Train"],
    [test_df, "Test"],
    target_feat="target"
)

# AVOID: Only analyzing training data
```


## 5. Control Pairwise Analysis


```python
# GOOD: Disable for speed on many features
report = sv.analyze(df, pairwise_analysis="off")  # Fast

# GOOD: Enable when feature correlations matter
report = sv.analyze(df, pairwise_analysis="on")   # Full correlations
```
