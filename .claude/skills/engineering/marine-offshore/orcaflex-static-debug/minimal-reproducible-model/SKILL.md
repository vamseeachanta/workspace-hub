---
name: orcaflex-static-debug-minimal-reproducible-model
description: 'Sub-skill of orcaflex-static-debug: Minimal Reproducible Model (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Minimal Reproducible Model (+1)

## Minimal Reproducible Model


When debugging, create a stripped-down model that isolates the failing component:

```python
import OrcFxAPI

def create_minimal_debug_model(failing_model_path, suspect_line_name):
    """Create a minimal model with only the suspect line for debugging."""
    model = OrcFxAPI.Model()
    model.LoadData(failing_model_path)

    # Remove all lines except the suspect
    for obj in list(model.objects):
        if obj.typeName == "Line" and obj.name != suspect_line_name:
            model.DestroyObject(obj)

    # Simplify environment
    env = model.environment
    env.WaveType = "None"

    # Save debug model
    debug_path = failing_model_path.replace(".yml", "_debug.yml")
    model.SaveData(debug_path)
    return debug_path
```


## YAML Debug Template


```yaml
# Minimal model for static debugging
General:
  WaterDepth: 1000
  StaticsDamping: 50
  StaticsMaxIterations: 200
  StaticsTolerance: 1e-4

Environment:
  WaveType: None
  RefCurrentSpeed: 0
  WindSpeed: 0

LineTypes:
  - Name: "Debug_Chain"
    Category: General
    OD: 0.084
    MassPerUnitLength: 145
    EA: 850000000
    EI: 0

Lines:
  - Name: "Debug_Line"
    LineType: ["Debug_Chain"]
    Length: [500]
    TargetSegmentLength: [10]
    EndAConnection: Anchored
    EndAX: -400
    EndAY: 0
    EndAZ: -1000
    EndBConnection: Fixed
    EndBX: 0
    EndBY: 0
    EndBZ: -20
```
