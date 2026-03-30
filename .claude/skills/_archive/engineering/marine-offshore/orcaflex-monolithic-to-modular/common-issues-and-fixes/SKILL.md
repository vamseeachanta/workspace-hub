---
name: orcaflex-monolithic-to-modular-common-issues-and-fixes
description: 'Sub-skill of orcaflex-monolithic-to-modular: Common Issues and Fixes.'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Common Issues and Fixes

## Common Issues and Fixes


| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Missing section in modular | Extractor doesn't map the YAML key | Add to `FIELD_TO_SECTION` or `SINGLETON_SECTIONS` |
| Property value lost | GenericObject subclass lacks typed field | Add field to schema class (Pydantic silent drop) |
| `None` vs missing diff | Builder skips None values | Use `model_fields_set` in `_merge_object()` |
| Boolean mismatch | SaveData() exports `True`/`False`, builder uses `"Yes"`/`"No"` | Use Python booleans in builder defaults |
| "Change not allowed" error | Dormant properties in re-loaded YAML | Use hardcoded safe defaults, not raw pass-through |
