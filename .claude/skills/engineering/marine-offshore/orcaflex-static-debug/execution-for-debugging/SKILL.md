---
name: orcaflex-static-debug-execution-for-debugging
description: 'Sub-skill of orcaflex-static-debug: Execution for Debugging.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Execution for Debugging

## Execution for Debugging


```python
import OrcFxAPI

# Progressive solver settings for convergence hunting
def find_convergence_settings(model_path):
    """Try progressively relaxed solver settings."""
    model = OrcFxAPI.Model()
    model.LoadData(model_path)

    settings = [
        {"damping": 10, "tolerance": 1e-5, "max_iter": 100},
        {"damping": 50, "tolerance": 1e-4, "max_iter": 200},
        {"damping": 100, "tolerance": 1e-3, "max_iter": 500},
        {"damping": 200, "tolerance": 1e-2, "max_iter": 1000},
    ]

    for s in settings:
        model.general.StaticsDamping = s["damping"]
        model.general.StaticsTolerance = s["tolerance"]
        model.general.StaticsMaxIterations = s["max_iter"]

        try:
            model.CalculateStatics()
            return {"converged": True, "settings": s}
        except OrcFxAPI.OrcaFlexError:
            continue

    return {"converged": False, "settings": None}
```
