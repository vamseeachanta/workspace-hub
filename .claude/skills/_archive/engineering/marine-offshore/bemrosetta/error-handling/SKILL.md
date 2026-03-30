---
name: bemrosetta-error-handling
description: 'Sub-skill of bemrosetta: Error Handling.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


```python
from digitalmodel.bemrosetta import (
    BEMRosettaError,
    ParserError,
    ConverterError,
    MeshError,
)

try:
    results = parser.parse("analysis.LIS")
except ParserError as e:
    print(f"Parse error: {e}")
    print(f"File: {e.context.get('file_path')}")
except BEMRosettaError as e:
    print(f"BEMRosetta error: {e}")
```
