---
name: orcaflex-installation-analysis-common-errors-and-fixes
description: 'Sub-skill of orcaflex-installation-analysis: Common Errors and Fixes
  (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Common Errors and Fixes (+3)

## Common Errors and Fixes


| Error | Cause | Fix |
|-------|-------|-----|
| `FileNotFoundError: reference_model_file` | Path to base model incorrect | Check `reference_model_file` and `reference_elevation_file` paths are relative to working directory |
| `KeyError: 'Key not found in line item'` | `length_index` doesn't match line sections | Count sections in reference model (0-indexed); verify `length_index` matches the section to extend |
| Static convergence fails at depth | Crane wire too short, structure below seabed, or tension too high | Check `delta_elevation` doesn't place structure below seabed; verify wire length = reference + abs(delta) |
| `6DBuoy position error` | InitialZ places buoy at impossible position | Verify reference elevation is correct; check for sign convention (negative = below sea level) |
| Model loads but simulation crashes | Environmental loads inappropriate for installation depth | Reduce wave Hs for splash zone cases; calm seas typical for installation |
| Crane wire tension exceeds capacity | Structure too heavy for depth or wire angle too steep | Add buoyancy aids; check structure submerged weight vs crane capacity |
| Sling connection breaks | Sling too short after depth change | Ensure intermediate slings are also updated with delta_elevation |

## Debugging Installation Models


```python
def diagnose_installation_model(model_path, expected_depth):
    """Check generated installation model for common issues."""
    import OrcFxAPI
    issues = []

    model = OrcFxAPI.Model()
    model.LoadData(model_path)
    wd = model.general.WaterDepth


*See sub-skills for full details.*

## Splash Zone Analysis Checklist


- [ ] Wave Hs appropriate for installation weather window (typically Hs < 2.5m)
- [ ] Fine depth increments through splash zone (1-2m steps)
- [ ] Hydrodynamic coefficients set for partially submerged structure
- [ ] Slamming loads considered (if applicable)
- [ ] Crane wire dynamic amplification factor applied
- [ ] Structure orientation at each depth is physical

## Validation


| Check | Method | Acceptable Range |
|-------|--------|-----------------|
| Crane wire tension | Extract from static results | < crane SWL with safety factor (typically SF > 2.0) |
| Structure elevation | Compare 6DBuoy Z with target | Within 0.1m of target delta_elevation |
| Wire length | Sum of wire sections | Reference length + abs(delta_elevation) +/- 1% |
| Sling tensions | Extract from static results | Positive (no compression in slings) |
| Static convergence | model.CalculateStatics() | Converges at all depths |
| Touchdown | Check structure Z vs seabed | Structure Z > -water_depth (not through seabed) |
