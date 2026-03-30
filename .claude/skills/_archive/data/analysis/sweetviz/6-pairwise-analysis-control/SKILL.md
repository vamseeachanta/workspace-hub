---
name: sweetviz-6-pairwise-analysis-control
description: 'Sub-skill of sweetviz: 6. Pairwise Analysis Control.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 6. Pairwise Analysis Control

## 6. Pairwise Analysis Control


**Controlling Correlation Analysis:**
```python
import sweetviz as sv
import pandas as pd
import numpy as np

np.random.seed(42)
n = 2000

# Dataset with many features
df = pd.DataFrame({
    f"feature_{i}": np.random.randn(n) for i in range(20)
})
df["target"] = np.random.choice([0, 1], n)

# Disable pairwise analysis for speed
report_fast = sv.analyze(
    source=df,
    target_feat="target",
    pairwise_analysis="off"  # Faster, no correlation matrix
)

# Enable pairwise analysis for full correlations
report_full = sv.analyze(
    source=df,
    target_feat="target",
    pairwise_analysis="on"  # Shows feature correlations
)

# Auto mode (default) - enables if < 20 features
report_auto = sv.analyze(
    source=df,
    target_feat="target",
    pairwise_analysis="auto"
)

report_full.show_html("full_pairwise.html")
```
