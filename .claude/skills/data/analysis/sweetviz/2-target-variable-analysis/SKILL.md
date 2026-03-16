---
name: sweetviz-2-target-variable-analysis
description: 'Sub-skill of sweetviz: 2. Target Variable Analysis.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 2. Target Variable Analysis

## 2. Target Variable Analysis


**Binary Target Analysis:**
```python
import sweetviz as sv
import pandas as pd
import numpy as np

# Create dataset with target variable
np.random.seed(42)
n = 3000

df = pd.DataFrame({
    "feature_1": np.random.randn(n),
    "feature_2": np.random.exponential(10, n),
    "feature_3": np.random.choice(["A", "B", "C"], n),
    "feature_4": np.random.randint(1, 100, n),
    "target": np.random.choice([0, 1], n, p=[0.7, 0.3])
})

# Analyze with target variable
# Shows how each feature relates to the target
report = sv.analyze(
    source=df,
    target_feat="target"  # Specify target column
)

report.show_html("target_analysis.html")
```

**Continuous Target Analysis:**
```python
import sweetviz as sv
import pandas as pd
import numpy as np

# Regression target example
np.random.seed(42)
n = 2000

# Features that affect the target
x1 = np.random.randn(n)
x2 = np.random.exponential(5, n)
x3 = np.random.choice([0, 1], n)

# Target is a function of features + noise
target = 10 + 2*x1 + 0.5*x2 + 3*x3 + np.random.randn(n)

df = pd.DataFrame({
    "feature_linear": x1,
    "feature_exp": x2,
    "feature_binary": x3,
    "feature_noise": np.random.randn(n),  # Unrelated feature
    "price": target  # Continuous target
})

# Analyze with continuous target
report = sv.analyze(
    source=df,
    target_feat="price"
)

report.show_html("regression_target_analysis.html")
```

**Multi-class Target:**
```python
import sweetviz as sv
import pandas as pd
import numpy as np

np.random.seed(42)
n = 2500

df = pd.DataFrame({
    "feature_1": np.random.randn(n),
    "feature_2": np.random.uniform(0, 100, n),
    "category": np.random.choice(["A", "B", "C"], n),
    "class_label": np.random.choice(
        ["Class_A", "Class_B", "Class_C", "Class_D"],
        n, p=[0.4, 0.3, 0.2, 0.1]
    )
})

# Multi-class target analysis
report = sv.analyze(
    source=df,
    target_feat="class_label"
)

report.show_html("multiclass_analysis.html")
```
