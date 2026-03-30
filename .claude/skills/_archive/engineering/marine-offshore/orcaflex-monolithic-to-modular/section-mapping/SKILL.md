---
name: orcaflex-monolithic-to-modular-section-mapping
description: 'Sub-skill of orcaflex-monolithic-to-modular: Section Mapping (+2).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Section Mapping (+2)

## Section Mapping


The extractor uses three mapping dicts from `schema/generic.py`:

| Mapping | Purpose | Example |
|---------|---------|---------|
| `FIELD_TO_SECTION` | spec field → OrcaFlex YAML key | `"line_types"` → `"LineTypes"` |
| `SINGLETON_SECTIONS` | singleton section → field | `"FrictionCoefficients"` → `"friction_coefficients"` |
| `TYPED_FIELD_MAP` | typed field → OrcaFlex prop | `"mass"` → `"Mass"` |


## Section Name Aliases


OrcaFlex `SaveData()` exports may use different section names than the API:

| YAML Export Name | API/Internal Name |
|-----------------|-------------------|
| `Groups` | `BrowserGroups` |
| `FrictionCoefficients` | `SolidFrictionCoefficients` |

The extractor handles both via `_SECTION_ALIASES` fallback in `_extract_singleton()`.


## Object Extraction Strategy


For each object in a list section:
1. Keys in `TYPED_FIELD_MAP` → extracted as typed Pydantic fields
2. All other keys → placed in `properties` dict (pass-through bag)
3. Both recombined by builder's `_merge_object()` during generation
