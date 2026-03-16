---
name: freecad-automation-extract-geometry-properties
description: 'Sub-skill of freecad-automation: Extract Geometry Properties (+2).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Extract Geometry Properties (+2)

## Extract Geometry Properties


```python
import FreeCAD
import Part

def extract_geometry_properties(doc_path):
    """Extract geometric properties from FreeCAD document."""
    doc = FreeCAD.openDocument(doc_path)
    results = {}

    for obj in doc.Objects:

*See sub-skills for full details.*

## Export Formats and CLI


```bash
# Export STEP from command line
freecadcmd -c "
import FreeCAD, Part
doc = FreeCAD.openDocument('model.FCStd')
Part.export(doc.Objects, 'output.step')
"

# Export STL
freecadcmd -c "
import FreeCAD, Mesh
doc = FreeCAD.openDocument('model.FCStd')
Mesh.export(doc.Objects, 'output.stl')
"
```

## Parse STEP/IGES Output Metadata


```python
import Part

def parse_export_stats(export_path):
    """Parse exported file and return statistics."""
    shape = Part.read(export_path)
    return {
        "solids": len(shape.Solids),
        "shells": len(shape.Shells),
        "faces": len(shape.Faces),

*See sub-skills for full details.*
