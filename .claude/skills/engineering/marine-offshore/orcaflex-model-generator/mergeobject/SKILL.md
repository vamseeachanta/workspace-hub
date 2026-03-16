---
name: orcaflex-model-generator-mergeobject
description: 'Sub-skill of orcaflex-model-generator: _merge_object() (+2).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# _merge_object() (+2)

## _merge_object()


Combines typed Pydantic fields with pass-through properties:

```python
@staticmethod
def _merge_object(obj: GenericObject) -> dict[str, Any]:
    merged = dict(obj.properties)           # 1. Start from properties bag
    explicitly_set = obj.model_fields_set    # 2. Track what was explicitly set

    for py_field, ofx_key in TYPED_FIELD_MAP.items():
        value = getattr(obj, py_field, None)
        if value is not None:
            merged[ofx_key] = value          # 3. Non-None typed fields override
        elif py_field in explicitly_set:
            merged[ofx_key] = value          # 4. Explicitly-set None preserved

    # 5. Priority keys first (Name, Category, ShapeType, etc.)
    ordered = {}
    for key in _PRIORITY_KEYS:
        if key in merged:
            ordered[key] = merged.pop(key)
    ordered.update(merged)
    return ordered
```


## Section Ordering (_SECTION_ORDER)


Critical: OrcaFlex validates references sequentially. Sections must appear in dependency order:

```
General → VariableData → ExpansionTables
→ RayleighDampingCoefficients, FrictionCoefficients, LineContactData
→ LineTypes, VesselTypes, ClumpTypes, StiffenerTypes, SupportTypes
→ Vessels, Lines, Shapes, 6DBuoys, 3DBuoys, Constraints, Links, Winches
→ MultibodyGroups, BrowserGroups, Groups
```


## Priority Keys (_PRIORITY_KEYS)


Mode-setting properties must appear before dependent properties within each object:

```python
_PRIORITY_KEYS = [
    "Name", "Category", "ShapeType", "Shape", "BuoyType",
    "Connection", "LinkType", "Geometry", "WaveType",
    "DegreesOfFreedomInStatics",
]
```
