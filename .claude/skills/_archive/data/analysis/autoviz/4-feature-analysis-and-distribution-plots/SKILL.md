---
name: autoviz-4-feature-analysis-and-distribution-plots
description: 'Sub-skill of autoviz: 4. Feature Analysis and Distribution Plots.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 4. Feature Analysis and Distribution Plots

## 4. Feature Analysis and Distribution Plots


**Understanding Feature Distributions:**
```python
from autoviz import AutoViz_Class
import pandas as pd
import numpy as np

# Create dataset with various distributions
np.random.seed(42)
df = pd.DataFrame({
    # Normal distribution
    "normal": np.random.normal(100, 15, 1000),

    # Skewed distribution
    "skewed": np.random.exponential(50, 1000),

    # Bimodal distribution
    "bimodal": np.concatenate([
        np.random.normal(30, 5, 500),
        np.random.normal(70, 5, 500)
    ]),

    # Uniform distribution
    "uniform": np.random.uniform(0, 100, 1000),

    # Categorical with different frequencies
    "category_balanced": np.random.choice(["A", "B", "C"], 1000),
    "category_imbalanced": np.random.choice(
        ["Common", "Rare", "Very Rare"],
        1000,
        p=[0.8, 0.15, 0.05]
    ),

    # Target variable
    "target": np.random.choice([0, 1], 1000, p=[0.7, 0.3])
})

AV = AutoViz_Class()

# AutoViz will automatically:
# 1. Detect distribution types
# 2. Create appropriate histograms
# 3. Show box plots for numerical features
# 4. Create bar charts for categorical features
# 5. Highlight potential outliers

df_analyzed = AV.AutoViz(
    filename="",
    dfte=df,
    depVar="target",
    verbose=2,
    chart_format="svg"
)
```

**Categorical Feature Analysis:**
```python
from autoviz import AutoViz_Class
import pandas as pd
import numpy as np

# Dataset with multiple categorical features
df = pd.DataFrame({
    "product_category": np.random.choice(
        ["Electronics", "Clothing", "Food", "Home", "Sports"],
        1000
    ),
    "customer_segment": np.random.choice(
        ["Premium", "Standard", "Budget"],
        1000,
        p=[0.2, 0.5, 0.3]
    ),
    "region": np.random.choice(
        ["North", "South", "East", "West"],
        1000
    ),
    "channel": np.random.choice(
        ["Online", "Store", "Mobile"],
        1000
    ),
    "revenue": np.random.exponential(500, 1000),
    "quantity": np.random.randint(1, 20, 1000)
})

AV = AutoViz_Class()

# AutoViz creates:
# - Bar charts for each categorical variable
# - Cross-tabulation visualizations
# - Category vs numerical variable plots

df_analyzed = AV.AutoViz(
    filename="",
    dfte=df,
    depVar="revenue",
    verbose=1,
    chart_format="png"
)
```
