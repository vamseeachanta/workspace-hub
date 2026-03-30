---
name: instrument-data-allotrope-installing-allotropy
description: 'Sub-skill of instrument-data-allotrope: Installing allotropy (+2).'
version: 1.0.0
category: science
type: reference
scripts_exempt: true
---

# Installing allotropy (+2)

## Installing allotropy

```bash
pip install allotropy --break-system-packages
```


## Handling parse failures

If allotropy native parsing fails:
1. Log the error for debugging
2. Fall back to flexible parser
3. Report reduced metadata completeness to user
4. Suggest exporting different format from instrument


## ASM Schema Validation

Validate output against Allotrope schemas when available:
```python
import jsonschema
# Schema URLs in references/asm_schema_overview.md
```
