---
name: data-validation-reporter-extend-validation-rules
description: 'Sub-skill of data-validation-reporter: Extend Validation Rules (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Extend Validation Rules (+1)

## Extend Validation Rules


```python
class CustomValidator(DataValidator):
    def _check_business_rules(self, df: pd.DataFrame) -> List[str]:
        """Add custom business logic validation."""
        issues = []

        # Example: Check date ranges
        if 'start_date' in df.columns and 'end_date' in df.columns:
            invalid_dates = (df['end_date'] < df['start_date']).sum()
            if invalid_dates > 0:
                issues.append(f'{invalid_dates} records with end_date before start_date')

        return issues
```

## Custom Visualizations


```python
# Add 5th panel to dashboard
fig = make_subplots(
    rows=3, cols=2,
    specs=[
        [{'type': 'indicator'}, {'type': 'bar'}],
        [{'type': 'bar'}, {'type': 'table'}],
        [{'type': 'scatter', 'colspan': 2}, None]  # New panel
    ]
)

*See sub-skills for full details.*
