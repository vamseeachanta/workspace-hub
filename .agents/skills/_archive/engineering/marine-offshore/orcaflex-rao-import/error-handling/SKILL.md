---
name: orcaflex-rao-import-error-handling
description: 'Sub-skill of orcaflex-rao-import: Error Handling.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


```python
from digitalmodel.marine_ops.marine_analysis.rao_processor import RAOImportError

try:
    rao_data = processor.import_from_aqwa("data/vessel.lis")
except RAOImportError as e:
    print(f"Import failed: {e}")
    print(f"Suggestions: {e.suggestions}")

except FileNotFoundError:
    print("AQWA file not found")

except ValueError as e:
    print(f"Data format error: {e}")
```
