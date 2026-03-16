---
name: autoviz-6-outlier-detection-and-highlighting
description: 'Sub-skill of autoviz: 6. Outlier Detection and Highlighting.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 6. Outlier Detection and Highlighting

## 6. Outlier Detection and Highlighting


**Automatic Outlier Identification:**
```python
from autoviz import AutoViz_Class
import pandas as pd
import numpy as np

# Create dataset with outliers
np.random.seed(42)
n = 1000

# Normal data with injected outliers
revenue = np.concatenate([
    np.random.normal(1000, 200, n - 20),  # Normal values
    np.random.uniform(3000, 5000, 10),    # High outliers
    np.random.uniform(-500, 0, 10)        # Low outliers
])

units = np.concatenate([
    np.random.normal(50, 10, n - 15),
    np.random.uniform(150, 200, 15)       # Outliers
])

df = pd.DataFrame({
    "revenue": revenue,
    "units": units,
    "cost": np.abs(revenue * 0.6 + np.random.randn(n) * 100),
    "category": np.random.choice(["A", "B", "C"], n),
    "region": np.random.choice(["North", "South", "East", "West"], n)
})

AV = AutoViz_Class()

# AutoViz automatically:
# 1. Detects outliers using IQR method
# 2. Highlights them in box plots
# 3. Shows them in scatter plots
# 4. Reports outlier counts

df_analyzed = AV.AutoViz(
    filename="",
    dfte=df,
    verbose=2,
    chart_format="svg"
)
```

**Custom Outlier Analysis Wrapper:**
```python
from autoviz import AutoViz_Class
import pandas as pd
import numpy as np

def analyze_with_outlier_report(df: pd.DataFrame, target: str = "") -> dict:
    """
    Run AutoViz and provide detailed outlier report.

    Args:
        df: Input DataFrame
        target: Target variable name (optional)

    Returns:
        Dictionary with analysis results and outlier info
    """
    # Calculate outliers before visualization
    outlier_info = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

        outlier_info[col] = {
            "count": len(outliers),
            "percentage": len(outliers) / len(df) * 100,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "min_outlier": outliers[col].min() if len(outliers) > 0 else None,
            "max_outlier": outliers[col].max() if len(outliers) > 0 else None
        }

    # Run AutoViz
    AV = AutoViz_Class()
    df_analyzed = AV.AutoViz(
        filename="",
        dfte=df,
        depVar=target,
        verbose=1,
        chart_format="png"
    )

    return {
        "analyzed_df": df_analyzed,
        "outlier_report": outlier_info,
        "total_outliers": sum(info["count"] for info in outlier_info.values())
    }

# Usage
# result = analyze_with_outlier_report(df, target="revenue")
# print(f"Total outliers found: {result['total_outliers']}")
```
