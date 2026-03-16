---
name: orcaflex-code-check-error-handling
description: 'Sub-skill of orcaflex-code-check: Error Handling.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


```python
try:
    results = check_mooring_safety_factors(tensions, mbl_values, "API_RP_2SK")
except ValueError as e:
    print(f"Unknown standard: {e}")
    print("Supported standards: API_RP_2SK, DNV_OS_E301, ISO_19901_7")

except KeyError as e:
    print(f"Missing data: {e}")
    print("Ensure all lines have MBL values defined")
```
