---
name: hydrodynamic-pipeline-checkpoint-1-mesh-quality
description: 'Sub-skill of hydrodynamic-pipeline: Checkpoint 1: Mesh Quality (+2).'
version: 1.0.1
category: engineering
type: reference
scripts_exempt: true
---

# Checkpoint 1: Mesh Quality (+2)

## Checkpoint 1: Mesh Quality


```python
def validate_panel_mesh(gdf_path, min_panels=200, max_aspect=3.0):
    """Validate panel mesh before diffraction analysis."""
    checks = {"passed": True, "issues": []}

    # Parse GDF and count panels
    # Check aspect ratios, normal directions, waterline closure
    # (implementation depends on mesh format)

    return checks
```


## Checkpoint 2: Diffraction Results


```python
def validate_diffraction_results(results):
    """Validate diffraction results before passing to OrcaFlex."""
    checks = {"passed": True, "issues": []}

    # RAO sanity checks
    heave_rao_at_long_period = results["raos"]["Heave"]["amplitude"][-1]
    if abs(heave_rao_at_long_period - 1.0) > 0.1:
        checks["issues"].append(
            f"Heave RAO at long period = {heave_rao_at_long_period:.3f} "
            "(expected ~1.0 — vessel should follow wave at low frequency)"
        )

    # Added mass should be positive on diagonal
    # Damping should be positive (energy dissipation)
    # Roll/pitch RAO should have clear resonance peak

    # Check for numerical issues
    for dof, data in results["raos"].items():
        if any(a > 100 for a in data["amplitude"]):
            checks["issues"].append(f"{dof} RAO has spikes > 100 — likely resonance without damping")
            checks["passed"] = False

    return checks
```


## Checkpoint 3: OrcaFlex Results


```python
def validate_orcaflex_moored_results(sim_path):
    """Validate final OrcaFlex simulation results."""
    import OrcFxAPI
    model = OrcFxAPI.Model()
    model.LoadSimulation(sim_path)
    checks = {"passed": True, "issues": []}

    # Check vessel offset
    vessel = model['FPSO']
    max_surge = max(abs(vessel.TimeHistory('X', OrcFxAPI.oeEndA)))
    if max_surge > 50:
        checks["issues"].append(f"Max surge = {max_surge:.1f}m — check mooring stiffness")

    # Check mooring tensions
    for obj in model.objects:
        if obj.typeName == 'Line' and 'Mooring' in obj.name:
            max_tension = max(obj.TimeHistory('Effective tension', OrcFxAPI.oeEndA))
            min_tension = min(obj.TimeHistory('Effective tension', OrcFxAPI.oeEndB))
            if min_tension < 0:
                checks["issues"].append(f"{obj.name}: negative tension (compression) — line may be slack")
                checks["passed"] = False

    return checks
```
