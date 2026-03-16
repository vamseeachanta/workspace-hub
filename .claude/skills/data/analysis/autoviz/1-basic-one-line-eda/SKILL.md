---
name: autoviz-1-basic-one-line-eda
description: 'Sub-skill of autoviz: 1. Basic One-Line EDA.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. Basic One-Line EDA

## 1. Basic One-Line EDA


**Simplest Usage:**
```python
from autoviz import AutoViz_Class

# Initialize AutoViz
AV = AutoViz_Class()

# Automatic visualization with one line
# Returns a dataframe and generates all charts
df_analyzed = AV.AutoViz(
    filename="data.csv",
    sep=",",
    depVar="",  # Target variable (optional)
    dfte=None,  # Pass DataFrame directly instead of filename
    header=0,
    verbose=1,  # 0=minimal, 1=medium, 2=detailed output
    lowess=False,
    chart_format="svg",
    max_rows_analyzed=150000,
    max_cols_analyzed=30
)

print(f"Analyzed {df_analyzed.shape[0]} rows, {df_analyzed.shape[1]} columns")
```

**From DataFrame:**
```python
from autoviz import AutoViz_Class
import pandas as pd

# Load your data
df = pd.read_csv("sales_data.csv")

# Or create sample data
df = pd.DataFrame({
    "revenue": [100, 200, 150, 300, 250, 400, 350, 500],
    "units": [10, 20, 15, 30, 25, 40, 35, 50],
    "category": ["A", "B", "A", "B", "A", "B", "A", "B"],
    "region": ["North", "South", "East", "West", "North", "South", "East", "West"],
    "profit": [20, 40, 30, 60, 50, 80, 70, 100],
    "customer_age": [25, 35, 45, 55, 30, 40, 50, 60]
})

# Initialize and visualize
AV = AutoViz_Class()

# Pass DataFrame directly using dfte parameter
df_result = AV.AutoViz(
    filename="",  # Empty when using dfte
    sep=",",
    depVar="profit",  # Optional: specify target variable
    dfte=df,
    header=0,
    verbose=1,
    chart_format="png"
)
```

**With Target Variable Analysis:**
```python
from autoviz import AutoViz_Class
import pandas as pd

# Classification dataset
df_classification = pd.DataFrame({
    "feature_1": [1.2, 2.3, 1.5, 3.4, 2.1, 4.5, 3.2, 5.1],
    "feature_2": [0.5, 1.2, 0.8, 2.1, 1.0, 3.2, 2.4, 4.0],
    "feature_3": ["low", "medium", "low", "high", "medium", "high", "medium", "high"],
    "target": [0, 0, 0, 1, 0, 1, 1, 1]
})

AV = AutoViz_Class()

# Specify target variable for focused analysis
df_analyzed = AV.AutoViz(
    filename="",
    sep=",",
    depVar="target",  # Target variable for classification
    dfte=df_classification,
    header=0,
    verbose=2,  # More detailed output
    chart_format="svg"
)

# Regression dataset
df_regression = pd.DataFrame({
    "size": [1000, 1500, 1200, 2000, 1800, 2500, 2200, 3000],
    "bedrooms": [2, 3, 2, 4, 3, 4, 4, 5],
    "location": ["urban", "suburban", "urban", "rural", "suburban", "rural", "suburban", "rural"],
    "age": [5, 10, 3, 15, 8, 20, 12, 25],
    "price": [200000, 280000, 220000, 350000, 300000, 380000, 340000, 420000]
})

# Analyze with continuous target
df_analyzed = AV.AutoViz(
    filename="",
    sep=",",
    depVar="price",  # Continuous target
    dfte=df_regression,
    header=0,
    verbose=1,
    chart_format="png"
)
```
