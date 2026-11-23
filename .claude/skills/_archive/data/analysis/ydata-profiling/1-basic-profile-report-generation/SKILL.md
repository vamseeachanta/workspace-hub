---
name: ydata-profiling-1-basic-profile-report-generation
description: 'Sub-skill of ydata-profiling: 1. Basic Profile Report Generation (+1).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. Basic Profile Report Generation (+1)

## 1. Basic Profile Report Generation


**Simplest Usage:**
```python
from ydata_profiling import ProfileReport
import pandas as pd

# Load data
df = pd.read_csv("data.csv")

# Generate profile report
profile = ProfileReport(df, title="Data Quality Report")

# Save to HTML file
profile.to_file("report.html")

# Display in Jupyter notebook
profile.to_notebook_iframe()
```

**With Configuration:**
```python
from ydata_profiling import ProfileReport
import pandas as pd

df = pd.read_csv("sales_data.csv")

# Customized profile report
profile = ProfileReport(
    df,
    title="Sales Data Quality Report",
    explorative=True,  # Enable all analyses
    dark_mode=False,
    orange_mode=False,
    config_file=None,  # Or path to custom config
    lazy=True  # Defer computation
)

# Access specific sections
print(profile.description_set)  # Variable descriptions
print(profile.get_description())  # Full description

# Save report
profile.to_file("sales_report.html")
```

**From DataFrame with Sample Data:**
```python
from ydata_profiling import ProfileReport
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create sample dataset
np.random.seed(42)
n = 5000

df = pd.DataFrame({
    "customer_id": range(1, n + 1),
    "name": [f"Customer_{i}" for i in range(n)],
    "age": np.random.normal(40, 15, n).astype(int),
    "income": np.random.exponential(50000, n),
    "category": np.random.choice(["A", "B", "C", "D"], n, p=[0.4, 0.3, 0.2, 0.1]),
    "registration_date": [
        datetime(2020, 1, 1) + timedelta(days=int(d))
        for d in np.random.uniform(0, 1825, n)
    ],
    "is_active": np.random.choice([True, False], n, p=[0.8, 0.2]),
    "score": np.random.uniform(0, 100, n),
    "email": [f"customer_{i}@example.com" for i in range(n)]
})

# Add some missing values
df.loc[np.random.choice(n, 200), "income"] = np.nan
df.loc[np.random.choice(n, 150), "age"] = np.nan

# Generate report
profile = ProfileReport(df, title="Customer Data Profile")
profile.to_file("customer_profile.html")
```


## 2. Variable Analysis


**Understanding Variable Types:**
```python
from ydata_profiling import ProfileReport
import pandas as pd
import numpy as np

# Dataset with various variable types
df = pd.DataFrame({
    # Numeric variables
    "integer_col": np.random.randint(1, 100, 1000),
    "float_col": np.random.randn(1000) * 100,

    # Categorical variables
    "category_high_card": [f"cat_{i}" for i in np.random.randint(1, 100, 1000)],
    "category_low_card": np.random.choice(["A", "B", "C"], 1000),

    # Boolean
    "boolean_col": np.random.choice([True, False], 1000),

    # Date/Time
    "date_col": pd.date_range("2020-01-01", periods=1000, freq="H"),

    # Text
    "text_col": ["Sample text " * np.random.randint(1, 10) for _ in range(1000)],

    # URL
    "url_col": [f"https://example.com/page/{i}" for i in range(1000)],

    # Constant
    "constant_col": ["constant"] * 1000,

    # Unique
    "unique_col": range(1000)
})

profile = ProfileReport(
    df,
    title="Variable Types Analysis",
    explorative=True
)

# The report will automatically detect:
# - Numeric: integer_col, float_col
# - Categorical: category_high_card, category_low_card
# - Boolean: boolean_col
# - DateTime: date_col
# - Text: text_col
# - URL: url_col
# - Constant: constant_col
# - Unique: unique_col (potentially ID column)

profile.to_file("variable_types_report.html")
```

**Detailed Variable Statistics:**
```python
from ydata_profiling import ProfileReport
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "revenue": np.random.exponential(1000, 5000),
    "quantity": np.random.randint(1, 100, 5000),
    "discount": np.random.uniform(0, 0.5, 5000),
    "category": np.random.choice(["Electronics", "Clothing", "Food"], 5000)
})

profile = ProfileReport(df, title="Sales Variables Analysis")

# Access variable-level statistics programmatically
description = profile.get_description()

# Numeric variable statistics
for var_name, var_data in description.variables.items():
    print(f"\n{var_name}:")
    print(f"  Type: {var_data['type']}")
    if "mean" in var_data:
        print(f"  Mean: {var_data['mean']:.2f}")
        print(f"  Std: {var_data['std']:.2f}")
        print(f"  Min: {var_data['min']:.2f}")
        print(f"  Max: {var_data['max']:.2f}")
```
