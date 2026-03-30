---
name: orcaflex-line-wizard-error-handling
description: 'Sub-skill of orcaflex-line-wizard: Error Handling.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Common Issues


```python
try:
    model.InvokeLineSetupWizard()
except OrcFxAPI.OrcaFlexError as e:
    error_msg = str(e)

    if "did not converge" in error_msg.lower():
        print("Wizard failed to converge")
        print("Try:")
        print("  - Increase MaxDamping")

*See sub-skills for full details.*
### Validation After Wizard


```python
def validate_wizard_results(model, configs):
    """Validate that wizard achieved targets."""
    model.CalculateStatics()

    validation = {"passed": True, "results": []}

    for config in configs:
        if not config.included:
            continue

*See sub-skills for full details.*
