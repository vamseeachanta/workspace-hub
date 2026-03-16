---
name: data-validation-reporter-basic-validation
description: 'Sub-skill of data-validation-reporter: Basic Validation (+2).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Basic Validation (+2)

## Basic Validation


```python
from data_validator import DataValidator
import pandas as pd

# Initialize with config
validator = DataValidator(config_path="config/validation.yaml")

# Load data
df = pd.read_csv("data/input.csv")


*See sub-skills for full details.*

## Generate Interactive Report


```python
from pathlib import Path

# Generate HTML report
validator.generate_interactive_report(
    validation_results=results,
    output_path=Path("reports/validation_report.html")
)

print("📊 Interactive report saved to reports/validation_report.html")
```

## Text Report


```python
# Generate text summary
text_report = validator.generate_report(results)
print(text_report)
```
