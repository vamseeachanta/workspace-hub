---
name: orcaflex-file-conversion-yaml-structure-validation
description: 'Sub-skill of orcaflex-file-conversion: YAML Structure Validation (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# YAML Structure Validation (+1)

## YAML Structure Validation


The converter validates:
- File is readable YAML
- Contains OrcaFlex-specific sections (General, Environment, etc.)
- File size is reasonable (> 100 bytes)
- No corruption during conversion

## Round-Trip Validation


```python
def validate_round_trip(original_dat: Path):
    """Validate .dat → .yml → .dat conversion."""
    import OrcFxAPI

    # Convert to YAML
    yml_file = original_dat.with_suffix('.yml')
    model1 = OrcFxAPI.Model(str(original_dat))
    model1.SaveData(str(yml_file))


*See sub-skills for full details.*
