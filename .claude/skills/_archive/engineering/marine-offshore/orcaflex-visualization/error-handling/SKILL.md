---
name: orcaflex-visualization-error-handling
description: 'Sub-skill of orcaflex-visualization: Error Handling.'
version: 1.1.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


```python
try:
    images = generate_model_views(sim_file, output_dir)
except OrcFxAPI.OrcaFlexError as e:
    print(f"OrcaFlex error: {e}")
    print("Check simulation file is valid")

except FileNotFoundError:
    print("Simulation file not found")
```
