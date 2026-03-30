---
name: autoviz-5-correlation-detection
description: 'Sub-skill of autoviz: 5. Correlation Detection.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 5. Correlation Detection

## 5. Correlation Detection


**Automatic Correlation Analysis:**
```python
from autoviz import AutoViz_Class
import pandas as pd
import numpy as np

# Create dataset with known correlations
np.random.seed(42)
n = 1000

# Base variables
x1 = np.random.randn(n)
x2 = np.random.randn(n)

df = pd.DataFrame({
    "x1": x1,
    "x2": x2,
    # Strongly correlated with x1
    "y1": x1 * 2 + np.random.randn(n) * 0.5,
    # Moderately correlated with x2
    "y2": x2 + np.random.randn(n) * 1.5,
    # Negatively correlated
    "y3": -x1 + np.random.randn(n) * 0.8,
    # No correlation
    "y4": np.random.randn(n),
    # Non-linear relationship
    "y5": x1 ** 2 + np.random.randn(n) * 0.5,
    # Target
    "target": (x1 + x2 > 0).astype(int)
})

AV = AutoViz_Class()

# AutoViz generates:
# 1. Correlation heatmap
# 2. Scatter plots for highly correlated pairs
# 3. Pair plots for feature relationships

df_analyzed = AV.AutoViz(
    filename="",
    dfte=df,
    depVar="target",
    verbose=2,
    chart_format="svg"
)
```

**Correlation with Lowess Smoothing:**
```python
from autoviz import AutoViz_Class
import pandas as pd
import numpy as np

# Dataset with non-linear relationships
np.random.seed(42)
x = np.linspace(0, 10, 500)

df = pd.DataFrame({
    "x": x,
    "linear": 2 * x + np.random.randn(500) * 2,
    "quadratic": x ** 2 + np.random.randn(500) * 5,
    "sinusoidal": 10 * np.sin(x) + np.random.randn(500) * 2,
    "logarithmic": 5 * np.log(x + 1) + np.random.randn(500),
    "target": x + np.random.randn(500)
})

AV = AutoViz_Class()

# Enable lowess smoothing to see trends
df_analyzed = AV.AutoViz(
    filename="",
    dfte=df,
    depVar="target",
    lowess=True,  # Enable lowess smoothing
    verbose=1,
    chart_format="png"
)
```
