---
name: orcaflex-vessel-setup-error-handling
description: 'Sub-skill of orcaflex-vessel-setup: Error Handling.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


```python
try:
    vessel_type = import_vessel_from_aqwa(model, aqwa_file, "Vessel_Type")
except OrcFxAPI.OrcaFlexError as e:
    print(f"Import failed: {e}")
    print("Check AQWA file path and format")

except FileNotFoundError:
    print("AQWA file not found")

except ValueError as e:
    print(f"Configuration error: {e}")
```
