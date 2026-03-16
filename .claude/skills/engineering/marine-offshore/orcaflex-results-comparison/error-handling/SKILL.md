---
name: orcaflex-results-comparison-error-handling
description: 'Sub-skill of orcaflex-results-comparison: Error Handling.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


```python
try:
    comparison = analyzer.compare_pretensions(configurations, targets)
except FileNotFoundError as e:
    print(f"Results file not found: {e}")
    print("Check configuration paths")

except KeyError as e:
    print(f"Variable not found: {e}")
    print("Check object and variable names match simulations")
```
