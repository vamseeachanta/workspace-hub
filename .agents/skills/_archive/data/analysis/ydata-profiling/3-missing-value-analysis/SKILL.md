---
name: ydata-profiling-3-missing-value-analysis
description: 'Sub-skill of ydata-profiling: 3. Missing Value Analysis (+1).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 3. Missing Value Analysis (+1)

## 3. Missing Value Analysis


**Detecting Missing Patterns:**
```python
from ydata_profiling import ProfileReport
import pandas as pd
import numpy as np

# Create dataset with various missing patterns
np.random.seed(42)
n = 5000

df = pd.DataFrame({
    "complete": np.random.randn(n),  # No missing

    "random_missing": np.where(
        np.random.random(n) < 0.1,
        np.nan,
        np.random.randn(n)
    ),

    "conditional_missing": np.where(
        np.random.randn(n) > 1.5,
        np.nan,
        np.random.randn(n)
    ),

    "block_missing": np.concatenate([
        np.random.randn(4000),
        np.full(1000, np.nan)
    ]),

    "highly_missing": np.where(
        np.random.random(n) < 0.7,
        np.nan,
        np.random.randn(n)
    )
})

# Profile with missing value analysis
profile = ProfileReport(
    df,
    title="Missing Value Analysis",
    missing_diagrams={
        "bar": True,
        "matrix": True,
        "heatmap": True
    }
)

profile.to_file("missing_analysis.html")

# Programmatic access to missing info
description = profile.get_description()
print("\nMissing Value Summary:")
for var_name, var_data in description.variables.items():
    missing_count = var_data.get("n_missing", 0)
    missing_pct = var_data.get("p_missing", 0) * 100
    print(f"  {var_name}: {missing_count} ({missing_pct:.1f}%)")
```

**Missing Value Configuration:**
```python
from ydata_profiling import ProfileReport
import pandas as pd

df = pd.read_csv("data_with_missing.csv")

# Detailed missing value analysis
profile = ProfileReport(
    df,
    title="Missing Value Deep Dive",
    missing_diagrams={
        "bar": True,     # Bar chart of missing values per variable
        "matrix": True,  # Nullity matrix (pattern visualization)
        "heatmap": True  # Nullity correlation heatmap
    },
    # Treat certain values as missing
    vars={
        "num": {
            "low_categorical_threshold": 0
        }
    }
)

profile.to_file("missing_deep_dive.html")
```


## 4. Correlation Analysis


**Multiple Correlation Methods:**
```python
from ydata_profiling import ProfileReport
import pandas as pd
import numpy as np

# Create correlated dataset
np.random.seed(42)
n = 2000

x1 = np.random.randn(n)
x2 = np.random.randn(n)

df = pd.DataFrame({
    "x1": x1,
    "x2": x2,
    "y_strong": x1 * 2 + np.random.randn(n) * 0.5,  # Strong correlation
    "y_moderate": x1 + np.random.randn(n) * 2,      # Moderate correlation
    "y_weak": x1 * 0.5 + np.random.randn(n) * 3,    # Weak correlation
    "y_negative": -x1 + np.random.randn(n) * 0.5,   # Negative correlation
    "y_nonlinear": x1 ** 2 + np.random.randn(n),    # Non-linear relationship
    "y_independent": np.random.randn(n),            # No correlation
    "category": np.random.choice(["A", "B", "C"], n)  # Categorical
})

# Profile with all correlation methods
profile = ProfileReport(
    df,
    title="Correlation Analysis",
    correlations={
        "pearson": {"calculate": True, "warn_high_correlations": 0.9},
        "spearman": {"calculate": True, "warn_high_correlations": 0.9},
        "kendall": {"calculate": True, "warn_high_correlations": 0.9},
        "phi_k": {"calculate": True, "warn_high_correlations": 0.9},
        "cramers": {"calculate": True, "warn_high_correlations": 0.9}
    }
)

profile.to_file("correlation_analysis.html")
```

**Correlation Thresholds:**
```python
from ydata_profiling import ProfileReport
import pandas as pd

df = pd.read_csv("features.csv")

# Custom correlation thresholds
profile = ProfileReport(
    df,
    title="Feature Correlation Report",
    correlations={
        "pearson": {
            "calculate": True,
            "warn_high_correlations": 0.8,  # Warn above this
            "threshold": 0.3  # Minimum to display
        },
        "spearman": {
            "calculate": True,
            "warn_high_correlations": 0.8
        }
    }
)

profile.to_file("feature_correlations.html")
```
