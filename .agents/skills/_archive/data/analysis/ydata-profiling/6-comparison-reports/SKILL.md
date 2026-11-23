---
name: ydata-profiling-6-comparison-reports
description: 'Sub-skill of ydata-profiling: 6. Comparison Reports.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 6. Comparison Reports

## 6. Comparison Reports


**Comparing Two Datasets:**
```python
from ydata_profiling import ProfileReport, compare
import pandas as pd
import numpy as np

# Create two related datasets
np.random.seed(42)

# Training data
df_train = pd.DataFrame({
    "feature_1": np.random.randn(5000),
    "feature_2": np.random.exponential(100, 5000),
    "feature_3": np.random.choice(["A", "B", "C"], 5000),
    "target": np.random.randint(0, 2, 5000)
})

# Test data (slightly different distribution)
df_test = pd.DataFrame({
    "feature_1": np.random.randn(2000) * 1.2,  # Different variance
    "feature_2": np.random.exponential(120, 2000),  # Different mean
    "feature_3": np.random.choice(["A", "B", "C", "D"], 2000),  # New category
    "target": np.random.randint(0, 2, 2000)
})

# Generate individual profiles
profile_train = ProfileReport(df_train, title="Training Data")
profile_test = ProfileReport(df_test, title="Test Data")

# Compare profiles
comparison = compare([profile_train, profile_test])

# Save comparison report
comparison.to_file("train_test_comparison.html")
```

**Before/After Comparison:**
```python
from ydata_profiling import ProfileReport, compare
import pandas as pd
import numpy as np

# Original data
df_before = pd.DataFrame({
    "value": np.concatenate([
        np.random.randn(900),
        np.array([100, -50, 200, 150, -100])  # Outliers
    ]),
    "category": np.random.choice(["A", "B", "C"], 905),
    "score": np.random.uniform(0, 100, 905)
})

# Add missing values
df_before.loc[np.random.choice(905, 50), "value"] = np.nan

# Cleaned data (after preprocessing)
df_after = df_before.copy()

# Remove outliers
Q1 = df_after["value"].quantile(0.25)
Q3 = df_after["value"].quantile(0.75)
IQR = Q3 - Q1
df_after = df_after[
    (df_after["value"] >= Q1 - 1.5 * IQR) &
    (df_after["value"] <= Q3 + 1.5 * IQR)
]

# Fill missing values
df_after["value"] = df_after["value"].fillna(df_after["value"].median())

# Compare before and after
profile_before = ProfileReport(df_before, title="Before Cleaning")
profile_after = ProfileReport(df_after, title="After Cleaning")

comparison = compare([profile_before, profile_after])
comparison.to_file("cleaning_comparison.html")
```
