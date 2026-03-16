---
name: sweetviz-3-dataset-comparison-compare
description: 'Sub-skill of sweetviz: 3. Dataset Comparison (Compare).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 3. Dataset Comparison (Compare)

## 3. Dataset Comparison (Compare)


**Train vs Test Comparison:**
```python
import sweetviz as sv
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# Create sample dataset
np.random.seed(42)
n = 5000

df = pd.DataFrame({
    "feature_1": np.random.randn(n),
    "feature_2": np.random.exponential(50, n),
    "feature_3": np.random.choice(["X", "Y", "Z"], n),
    "feature_4": np.random.randint(1, 100, n),
    "target": np.random.choice([0, 1], n, p=[0.75, 0.25])
})

# Split into train and test
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

print(f"Train shape: {train_df.shape}")
print(f"Test shape: {test_df.shape}")

# Compare train vs test datasets
comparison_report = sv.compare(
    source=[train_df, "Training Data"],
    compare=[test_df, "Test Data"],
    target_feat="target"
)

comparison_report.show_html("train_test_comparison.html")
```

**Before vs After Comparison:**
```python
import sweetviz as sv
import pandas as pd
import numpy as np

np.random.seed(42)

# Original data with issues
df_before = pd.DataFrame({
    "value": np.concatenate([
        np.random.randn(900),
        np.array([50, -30, 100, 75, -50])  # Outliers
    ]),
    "category": np.random.choice(["A", "B", "C"], 905),
    "score": np.random.uniform(0, 100, 905)
})

# Add missing values
df_before.loc[np.random.choice(905, 80), "value"] = np.nan

# Cleaned data
df_after = df_before.copy()

# Remove outliers using IQR
Q1 = df_after["value"].quantile(0.25)
Q3 = df_after["value"].quantile(0.75)
IQR = Q3 - Q1
df_after = df_after[
    (df_after["value"].isna()) |  # Keep NaN for now
    ((df_after["value"] >= Q1 - 1.5 * IQR) &
     (df_after["value"] <= Q3 + 1.5 * IQR))
]

# Fill missing values
df_after["value"] = df_after["value"].fillna(df_after["value"].median())

# Compare before vs after cleaning
comparison = sv.compare(
    source=[df_before, "Before Cleaning"],
    compare=[df_after, "After Cleaning"]
)

comparison.show_html("cleaning_comparison.html")
```

**Production vs Development Data:**
```python
import sweetviz as sv
import pandas as pd
import numpy as np

np.random.seed(42)

# Development data (historical)
df_dev = pd.DataFrame({
    "feature_1": np.random.randn(3000),
    "feature_2": np.random.exponential(100, 3000),
    "category": np.random.choice(["A", "B", "C"], 3000, p=[0.5, 0.3, 0.2])
})

# Production data (slightly different distribution - data drift)
df_prod = pd.DataFrame({
    "feature_1": np.random.randn(1000) * 1.2 + 0.3,  # Shifted and scaled
    "feature_2": np.random.exponential(120, 1000),    # Different mean
    "category": np.random.choice(["A", "B", "C", "D"], 1000, p=[0.4, 0.3, 0.2, 0.1])  # New category
})

# Detect data drift
drift_report = sv.compare(
    source=[df_dev, "Development"],
    compare=[df_prod, "Production"]
)

drift_report.show_html("data_drift_analysis.html")
```
