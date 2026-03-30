---
name: orcaflex-line-wizard-common-errors-and-fixes
description: 'Sub-skill of orcaflex-line-wizard: Common Errors and Fixes (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Common Errors and Fixes (+1)

## Common Errors and Fixes


| Error | Cause | Fix |
|-------|-------|-----|
| `Wizard did not converge` | Target tension unachievable with current line geometry | Increase `MaxDamping` (try 50, 100, 200); check target is physically possible |
| `Line not found` | Line name in config doesn't match model | Check exact spelling and case of line names in model |
| `Singular Jacobian` | Too many lines configured simultaneously | Reduce number of included lines; solve in batches |
| Wizard converges but tension wrong | Wrong `LineEnd` specified (End A vs End B) | Verify which end connects to vessel (usually End A for fairlead tension) |
| Length becomes negative | Target tension too low for line weight | Increase target tension above minimum catenary tension |
| Wizard changes wrong section | `length_index` not targeting the adjustable section | Verify which section should change length (typically the longest segment) |

## Debugging Wizard Failures


```python
def diagnose_wizard_failure(model, line_name, target_tension):
    """Diagnose why Line Setup Wizard fails for a specific line."""
    line = model[line_name]
    issues = []

    # Check line is properly connected
    end_a = line.EndAConnection
    end_b = line.EndBConnection
    if end_a == "Free" and end_b == "Free":

*See sub-skills for full details.*
