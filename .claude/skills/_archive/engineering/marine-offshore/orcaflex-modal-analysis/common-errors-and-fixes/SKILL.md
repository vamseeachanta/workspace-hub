---
name: orcaflex-modal-analysis-common-errors-and-fixes
description: 'Sub-skill of orcaflex-modal-analysis: Common Errors and Fixes (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Common Errors and Fixes (+1)

## Common Errors and Fixes


| Error | Cause | Fix |
|-------|-------|-----|
| `Statics failed to converge` | Model not in equilibrium before modal | Fix statics first (see orcaflex-static-debug skill) |
| `Singular stiffness matrix` | Zero-tension lines or disconnected components | Check all lines have positive tension; verify all connections |
| `No modes found` | lastMode too low or model too simple | Increase `lastMode`; add more DOFs (finer segmentation) |
| Modal analysis hangs | Very large model with too many modes requested | Reduce `lastMode` or simplify model (coarser segments) |
| Unrealistic frequencies | Wrong units (mass, stiffness) or missing added mass | Verify line type properties; check hydrodynamic coefficients |
| Mode shapes all zero for an object | Object not included in modal analysis scope | Add object to `ObjectName` list in config |
| Duplicate frequencies | Symmetric model produces paired modes | Expected for symmetric configurations; modes are degenerate pairs |

## Debugging Modal Issues


```python
def diagnose_modal_failure(model):
    """Pre-check model before modal analysis."""
    issues = []

    # Check statics first
    try:
        model.CalculateStatics()
    except OrcFxAPI.OrcaFlexError as e:
        issues.append(f"Statics failed: {e} — fix statics before modal analysis")

*See sub-skills for full details.*
