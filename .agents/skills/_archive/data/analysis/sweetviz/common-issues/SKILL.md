---
name: sweetviz-common-issues
description: 'Sub-skill of sweetviz: Common Issues.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: Report generation is slow**
```python
# Solution 1: Disable pairwise analysis
report = sv.analyze(df, pairwise_analysis="off")

# Solution 2: Sample data
report = sv.analyze(df.sample(50000))

# Solution 3: Skip high-cardinality columns
config = sv.FeatureConfig(skip=["high_card_col"])
report = sv.analyze(df, feat_cfg=config)
```

**Issue: Memory error with large dataset**
```python
# Solution: Process in chunks or sample
sample_size = min(len(df), 100000)
report = sv.analyze(df.sample(sample_size, random_state=42))
```

**Issue: HTML report won't open**
```python
# Solution: Save and open manually
report.show_html("report.html", open_browser=False)
# Then open report.html in browser

# Or specify layout
report.show_html("report.html", layout="vertical")
```

**Issue: Categorical variables treated as numeric**
```python
# Solution: Force categorical type
config = sv.FeatureConfig(force_cat=["zip_code", "rating"])
report = sv.analyze(df, feat_cfg=config)

# Or convert before analysis
df["zip_code"] = df["zip_code"].astype(str)
```

**Issue: Date columns not recognized**
```python
# Solution: Convert to proper datetime
df["date_col"] = pd.to_datetime(df["date_col"])
report = sv.analyze(df)
```

**Issue: Report shows too many categories**
```python
# Sweetviz automatically limits to top categories
# For custom handling, reduce cardinality before analysis
df["category"] = df["category"].apply(
    lambda x: x if x in top_categories else "Other"
)
```
