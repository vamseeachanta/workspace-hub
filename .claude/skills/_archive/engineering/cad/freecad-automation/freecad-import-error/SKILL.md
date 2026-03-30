---
name: freecad-automation-freecad-import-error
description: 'Sub-skill of freecad-automation: FreeCAD Import Error (+1).'
version: 2.0.0
category: engineering
type: reference
scripts_exempt: true
---

# FreeCAD Import Error (+1)

## FreeCAD Import Error


```python
# Add FreeCAD to Python path
import sys
sys.path.append('/path/to/FreeCAD/lib')
```

## Memory Issues


```python
# Reduce parallel workers for large files
agent = FreeCADAgent(config={
    "settings": {
        "parallel_workers": 2,
        "memory_limit_mb": 2048
    }
})
```
