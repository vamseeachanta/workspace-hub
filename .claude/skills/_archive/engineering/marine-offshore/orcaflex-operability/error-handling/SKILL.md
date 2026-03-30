---
name: orcaflex-operability-error-handling
description: 'Sub-skill of orcaflex-operability: Error Handling.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


```python
try:
    envelope = analyzer.generate_operability_envelope(...)
except FileNotFoundError as e:
    print(f"Simulation files not found: {e}")
    print("Check simulation_directory and file_pattern")

except ValueError as e:
    print(f"Configuration error: {e}")
    print("Check line names and variable specifications")
```
