---
name: freecad-automation-common-failures
description: 'Sub-skill of freecad-automation: Common Failures (+2).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Common Failures (+2)

## Common Failures


| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'FreeCAD'` | FreeCAD not in Python path | Add to path: `sys.path.append('/usr/lib/freecad-daily/lib')` or use `freecadcmd` |
| `FreeCAD.openDocument(): file not found` | Wrong path or .FCStd corrupted | Check path; try opening in GUI first |
| `Part.BRepBuilderAPI: shape is not valid` | Invalid geometry (self-intersection) | Run `shape.fix(0.1, 0.1, 0.1)` or simplify geometry |
| `Mesh export produces 0-byte STL` | No mesh-compatible objects | Ensure objects have Shape; use Part before Mesh export |
| `Boolean operation failed` | Overlapping/touching geometry | Add small offset (0.01mm) between bodies; check geometry validity |
| `Recompute failed` | Sketches over-/under-constrained | Check `obj.Shape.isValid()` and sketch DOF count |
| `ImportError: No module named 'FreeCADGui'` | Running headless without GUI module (FreeCAD < 0.21) | FreeCAD ≥ 0.21: `freecadcmd` includes FreeCADGui (no-op window); safe to import. FreeCAD < 0.21: use `freecadcmd` and avoid Gui-dependent operations |

## Diagnostic Function


```python
import FreeCAD

def diagnose_freecad_model(doc_path):
    """Diagnose common FreeCAD model issues."""
    diag = {"issues": [], "warnings": [], "info": []}

    try:
        doc = FreeCAD.openDocument(doc_path)
    except Exception as e:

*See sub-skills for full details.*

## Headless Execution Troubleshooting


```bash
# FreeCAD headless (no GUI)
freecadcmd script.py

# If freecadcmd not found, use full path
/usr/bin/freecadcmd script.py

# Alternative: use FreeCAD with -c flag
freecad -c "exec(open('script.py').read())"

# Check FreeCAD Python path
python3 -c "import sys; sys.path.append('/usr/lib/freecad-daily/lib'); import FreeCAD; print(FreeCAD.Version())"
```

> **Note (FreeCAD ≥ 0.21):** `freecadcmd` includes `FreeCADGui` as a no-op stub — `import FreeCADGui` succeeds but GUI operations are non-functional. Safe to use in scripts that conditionally check for GUI availability.
