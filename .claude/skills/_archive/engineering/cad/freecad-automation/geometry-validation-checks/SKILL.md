---
name: freecad-automation-geometry-validation-checks
description: 'Sub-skill of freecad-automation: Geometry Validation Checks (+1).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Geometry Validation Checks (+1)

## Geometry Validation Checks


```python
def validate_geometry(doc_path, expected=None):
    """Validate FreeCAD geometry against expected parameters."""
    import FreeCAD
    import Part

    checks = {"passed": True, "issues": []}
    doc = FreeCAD.openDocument(doc_path)

    for obj in doc.Objects:

*See sub-skills for full details.*

## Export Round-Trip Validation


```python
def validate_step_export(original_fcstd, exported_step):
    """Validate STEP export by comparing with original."""
    import FreeCAD
    import Part

    # Read original
    doc = FreeCAD.openDocument(original_fcstd)
    original_volume = sum(
        o.Shape.Volume for o in doc.Objects if hasattr(o, 'Shape') and o.Shape.Volume > 0

*See sub-skills for full details.*
