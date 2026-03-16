---
name: orcaflex-yaml-gotchas-safe-yaml-builder-pattern
description: 'Sub-skill of orcaflex-yaml-gotchas: Safe YAML Builder Pattern (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Safe YAML Builder Pattern (+1)

## Safe YAML Builder Pattern


When generating OrcaFlex YAML programmatically, use this pattern to avoid dormant property traps:

```python
def build_environment_section(spec):
    """Build environment YAML with safe defaults first, then overlay."""
    # Start with safe defaults that won't trigger dormant property errors
    env = {
        "SeabedModel": "Elastic",
        "MultipleCurrentDataCanBeDefined": False,
        "CurrentModel": "Variation scheme",
        "WindType": "Constant",
        "WaveType": "None",
    }

    # Overlay specific values from spec
    if spec.waves:
        env["WaveType"] = spec.waves.type
        if spec.waves.type in ("JONSWAP", "Pierson-Moskowitz"):
            env["WaveHs"] = spec.waves.Hs
            env["WaveTp"] = spec.waves.Tp
            if spec.waves.type == "JONSWAP":
                env["WaveGamma"] = spec.waves.gamma

    return {"Environment": env}
```


## Section Ordering Template


```python
# Emit sections in this order to avoid reference errors
_SECTION_ORDER = [
    "General", "VariableData", "ExpansionTables",
    "RayleighDampingCoefficients", "FrictionCoefficients", "LineContactData",
    "LineTypes", "VesselTypes", "ClumpTypes", "StiffenerTypes", "SupportTypes",
    "Vessels", "Lines", "Shapes", "6DBuoys", "3DBuoys",
    "Constraints", "Links", "Winches", "FlexJoints",
    "MultibodyGroups", "BrowserGroups", "Groups",
]

def order_sections(model_dict):
    """Reorder model dict to match OrcaFlex dependency order."""
    ordered = {}
    for key in _SECTION_ORDER:
        if key in model_dict:
            ordered[key] = model_dict[key]
    # Append any unknown sections at the end
    for key in model_dict:
        if key not in ordered:
            ordered[key] = model_dict[key]
    return ordered
```
