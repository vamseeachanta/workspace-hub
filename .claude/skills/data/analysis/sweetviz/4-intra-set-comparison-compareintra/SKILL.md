---
name: sweetviz-4-intra-set-comparison-compareintra
description: 'Sub-skill of sweetviz: 4. Intra-set Comparison (Compare_Intra) (+1).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 4. Intra-set Comparison (Compare_Intra) (+1)

## 4. Intra-set Comparison (Compare_Intra)


**Compare Subpopulations Within Dataset:**
```python
import sweetviz as sv
import pandas as pd
import numpy as np

np.random.seed(42)
n = 4000

# Create dataset with a categorical variable for splitting
df = pd.DataFrame({
    "age": np.random.randint(18, 70, n),
    "income": np.random.exponential(50000, n),
    "purchases": np.random.poisson(10, n),
    "satisfaction_score": np.random.uniform(1, 5, n),
    "customer_type": np.random.choice(["Premium", "Standard"], n, p=[0.3, 0.7]),
    "churned": np.random.choice([0, 1], n, p=[0.85, 0.15])
})

# Compare Premium vs Standard customers within same dataset
intra_report = sv.compare_intra(
    source_df=df,
    condition_series=df["customer_type"] == "Premium",
    names=["Premium Customers", "Standard Customers"],
    target_feat="churned"
)

intra_report.show_html("customer_type_comparison.html")
```

**Compare by Boolean Condition:**
```python
import sweetviz as sv
import pandas as pd
import numpy as np

np.random.seed(42)
n = 3000

df = pd.DataFrame({
    "age": np.random.randint(18, 80, n),
    "income": np.random.exponential(60000, n),
    "credit_score": np.random.normal(700, 50, n).astype(int),
    "loan_amount": np.random.exponential(20000, n),
    "default": np.random.choice([0, 1], n, p=[0.9, 0.1])
})

# Compare high-income vs low-income customers
median_income = df["income"].median()

income_comparison = sv.compare_intra(
    source_df=df,
    condition_series=df["income"] > median_income,
    names=["High Income", "Low Income"],
    target_feat="default"
)

income_comparison.show_html("income_segment_comparison.html")
```

**Multiple Segment Analysis:**
```python
import sweetviz as sv
import pandas as pd
import numpy as np

np.random.seed(42)
n = 5000

df = pd.DataFrame({
    "age": np.random.randint(18, 80, n),
    "spend": np.random.exponential(500, n),
    "visits": np.random.poisson(5, n),
    "region": np.random.choice(["North", "South", "East", "West"], n),
    "converted": np.random.choice([0, 1], n, p=[0.8, 0.2])
})

# Create age groups
df["age_group"] = pd.cut(
    df["age"],
    bins=[0, 30, 50, 100],
    labels=["Young", "Middle", "Senior"]
)

# Compare Young vs Senior (Middle excluded)
age_comparison = sv.compare_intra(
    source_df=df,
    condition_series=df["age_group"] == "Young",
    names=["Young (18-30)", "Senior (50+)"],
    target_feat="converted"
)

age_comparison.show_html("age_group_comparison.html")
```


## 5. Feature Configuration


**Specifying Feature Types:**
```python
import sweetviz as sv
import pandas as pd
import numpy as np

np.random.seed(42)
n = 2000

df = pd.DataFrame({
    "id": range(1, n + 1),
    "zip_code": np.random.randint(10000, 99999, n),  # Should be categorical
    "rating": np.random.randint(1, 6, n),  # Ordinal (1-5 stars)
    "revenue": np.random.exponential(1000, n),
    "category": np.random.choice(["A", "B", "C"], n),
    "target": np.random.choice([0, 1], n)
})

# Configure feature types
feature_config = sv.FeatureConfig(
    skip=["id"],  # Skip ID column
    force_cat=["zip_code", "rating"],  # Force as categorical
    force_num=[]  # Force as numerical (if needed)
)

report = sv.analyze(
    source=df,
    target_feat="target",
    feat_cfg=feature_config
)

report.show_html("configured_analysis.html")
```

**Skipping Features:**
```python
import sweetviz as sv
import pandas as pd
import numpy as np

np.random.seed(42)
n = 1500

df = pd.DataFrame({
    "user_id": range(n),
    "session_id": [f"sess_{i}" for i in range(n)],
    "email": [f"user_{i}@example.com" for i in range(n)],
    "feature_1": np.random.randn(n),
    "feature_2": np.random.exponential(10, n),
    "outcome": np.random.choice([0, 1], n)
})

# Skip ID and PII columns
config = sv.FeatureConfig(
    skip=["user_id", "session_id", "email"]
)

report = sv.analyze(
    source=df,
    target_feat="outcome",
    feat_cfg=config
)

report.show_html("filtered_analysis.html")
```
