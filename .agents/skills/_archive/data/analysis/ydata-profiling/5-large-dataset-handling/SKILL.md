---
name: ydata-profiling-5-large-dataset-handling
description: 'Sub-skill of ydata-profiling: 5. Large Dataset Handling.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 5. Large Dataset Handling

## 5. Large Dataset Handling


**Minimal Mode for Speed:**
```python
from ydata_profiling import ProfileReport
import pandas as pd
import numpy as np

# Large dataset
large_df = pd.DataFrame({
    f"col_{i}": np.random.randn(1000000)
    for i in range(50)
})
large_df["category"] = np.random.choice(["A", "B", "C"], 1000000)

print(f"Dataset size: {large_df.shape}")

# Minimal mode - fast but less detailed
profile = ProfileReport(
    large_df,
    title="Large Dataset Profile",
    minimal=True  # Enables minimal mode
)

profile.to_file("large_dataset_minimal.html")
```

**Sampling for Large Datasets:**
```python
from ydata_profiling import ProfileReport
import pandas as pd
import numpy as np

def profile_large_dataset(
    df: pd.DataFrame,
    sample_size: int = 100000,
    title: str = "Sampled Profile"
) -> ProfileReport:
    """
    Profile large dataset using sampling.

    Args:
        df: Input DataFrame
        sample_size: Number of rows to sample
        title: Report title

    Returns:
        ProfileReport object
    """
    if len(df) > sample_size:
        df_sampled = df.sample(n=sample_size, random_state=42)
        print(f"Sampled {sample_size} rows from {len(df)}")
    else:
        df_sampled = df
        print(f"Using full dataset: {len(df)} rows")

    return ProfileReport(
        df_sampled,
        title=f"{title} (n={len(df_sampled):,})",
        minimal=len(df_sampled) > 50000  # Auto minimal for large samples
    )

# Usage
# large_df = pd.read_parquet("huge_dataset.parquet")
# profile = profile_large_dataset(large_df, sample_size=50000)
# profile.to_file("sampled_profile.html")
```

**Explorative vs Minimal Configuration:**
```python
from ydata_profiling import ProfileReport
import pandas as pd

df = pd.read_csv("data.csv")

# EXPLORATIVE MODE - Full analysis (slower)
profile_full = ProfileReport(
    df,
    title="Full Explorative Report",
    explorative=True,  # Enable all analyses
    correlations={
        "pearson": {"calculate": True},
        "spearman": {"calculate": True},
        "kendall": {"calculate": True},
        "phi_k": {"calculate": True}
    },
    missing_diagrams={
        "bar": True,
        "matrix": True,
        "heatmap": True
    },
    interactions={
        "continuous": True  # Scatter plots for numeric pairs
    }
)

# MINIMAL MODE - Quick overview (faster)
profile_minimal = ProfileReport(
    df,
    title="Minimal Quick Report",
    minimal=True,  # Disable expensive computations
    correlations=None,  # Skip correlations
    missing_diagrams={"bar": False, "matrix": False, "heatmap": False},
    interactions={"continuous": False}
)
```
