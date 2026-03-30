---
name: orcaflex-extreme-analysis-error-handling
description: 'Sub-skill of orcaflex-extreme-analysis: Error Handling.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


```python
try:
    results = extractor.extract_linked_statistics(sim_file, config)
except OrcFxAPI.OrcaFlexError as e:
    print(f"OrcaFlex error: {e}")
    print("Check object names and variable specifications")

except FileNotFoundError:
    print("Simulation file not found")
```
