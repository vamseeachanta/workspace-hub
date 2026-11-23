---
name: sweetviz-1-basic-eda-report-analyze
description: 'Sub-skill of sweetviz: 1. Basic EDA Report (Analyze).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. Basic EDA Report (Analyze)

## 1. Basic EDA Report (Analyze)


**Single Dataset Analysis:**
```python
import sweetviz as sv
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv("data.csv")

# Generate basic EDA report
report = sv.analyze(df)

# Save HTML report
report.show_html("sweetviz_report.html")

# Show in notebook (auto-opens browser)
report.show_notebook()
```

**With Source Name:**
```python
import sweetviz as sv
import pandas as pd

df = pd.read_csv("sales_data.csv")

# Generate report with custom name
report = sv.analyze(
    source=df,
    pairwise_analysis="auto"  # "on", "off", or "auto"
)

report.show_html("sales_analysis.html", open_browser=True)
```

**Sample Dataset for Examples:**
```python
import sweetviz as sv
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create comprehensive sample dataset
np.random.seed(42)
n = 5000

df = pd.DataFrame({
    # Numeric features
    "age": np.random.randint(18, 80, n),
    "income": np.random.exponential(50000, n),
    "credit_score": np.random.normal(700, 50, n).clip(300, 850).astype(int),
    "account_balance": np.random.exponential(10000, n),
    "transaction_count": np.random.poisson(15, n),

    # Categorical features
    "gender": np.random.choice(["Male", "Female", "Other"], n, p=[0.48, 0.48, 0.04]),
    "education": np.random.choice(
        ["High School", "Bachelor", "Master", "PhD"],
        n, p=[0.3, 0.4, 0.2, 0.1]
    ),
    "employment_status": np.random.choice(
        ["Employed", "Self-employed", "Unemployed", "Retired"],
        n, p=[0.6, 0.2, 0.1, 0.1]
    ),
    "region": np.random.choice(["North", "South", "East", "West"], n),

    # Date feature
    "join_date": [
        datetime(2020, 1, 1) + timedelta(days=int(d))
        for d in np.random.uniform(0, 1460, n)
    ],

    # Target variable (binary classification)
    "churned": np.random.choice([0, 1], n, p=[0.8, 0.2])
})

# Add some missing values
df.loc[np.random.choice(n, 200), "income"] = np.nan
df.loc[np.random.choice(n, 100), "credit_score"] = np.nan
df.loc[np.random.choice(n, 150), "education"] = np.nan

# Basic analysis
report = sv.analyze(df)
report.show_html("customer_analysis.html")
```
