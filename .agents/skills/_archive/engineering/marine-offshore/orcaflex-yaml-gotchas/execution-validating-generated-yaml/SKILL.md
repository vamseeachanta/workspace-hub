---
name: orcaflex-yaml-gotchas-execution-validating-generated-yaml
description: 'Sub-skill of orcaflex-yaml-gotchas: Execution: Validating Generated
  YAML.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Execution: Validating Generated YAML

## Execution: Validating Generated YAML


```python
import OrcFxAPI

def validate_yaml_round_trip(yaml_path):
    """Load YAML into OrcFxAPI and check for errors."""
    model = OrcFxAPI.Model()
    try:
        model.LoadData(yaml_path)
        return {"valid": True, "errors": []}
    except OrcFxAPI.OrcaFlexError as e:
        error_msg = str(e)
        errors = [error_msg]

        # Diagnose common YAML gotchas
        if "Change not allowed" in error_msg:
            errors.append("Likely dormant property issue — check mode-setting property order")
        if "not a valid" in error_msg and "name" in error_msg.lower():
            errors.append("Reference to undefined object — check section ordering")
        if "alias" in error_msg.lower():
            errors.append("YAML aliases not supported — use NoAliasDumper")

        return {"valid": False, "errors": errors}
```
