---
name: orcawave-analysis-license-issues
description: 'Sub-skill of orcawave-analysis: License Issues (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# License Issues (+1)

## License Issues


```python
# Check license before batch
from digitalmodel.orcawave.license import check_orcawave_license

if not check_orcawave_license():
    print("Waiting for license...")
    wait_for_license(timeout=3600)  # Wait up to 1 hour
```

## Mesh Issues


```python
# Validate mesh before analysis
from digitalmodel.orcawave.mesh import validate_panel_mesh

validation = validate_panel_mesh("geometry/hull_panels.dat")
if validation["issues"]:
    for issue in validation["issues"]:
        print(f"Mesh issue: {issue}")
```
