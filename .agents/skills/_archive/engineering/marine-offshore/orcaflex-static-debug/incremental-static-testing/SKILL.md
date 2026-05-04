---
name: orcaflex-static-debug-incremental-static-testing
description: 'Sub-skill of orcaflex-static-debug: Incremental Static Testing (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Incremental Static Testing (+1)

## Incremental Static Testing


```python
def test_static_incrementally(model_path: str) -> dict:
    """
    Test static analysis by progressively enabling components.

    Returns which component causes failure.
    """
    model = OrcFxAPI.Model()
    model.LoadData(model_path)

    results = {"tests": [], "failing_component": None}

    # Get all lines
    lines = [obj for obj in model.objects if obj.typeName == "Line"]

    # Disable all lines
    for line in lines:
        line.IncludedInStatics = "No"

    # Test with no lines
    try:
        model.CalculateStatics()
        results["tests"].append({"component": "Base model (no lines)", "passed": True})
    except Exception as e:
        results["tests"].append({"component": "Base model", "passed": False, "error": str(e)})
        results["failing_component"] = "Base model"
        return results

    # Enable lines one by one
    for line in lines:
        line.IncludedInStatics = "Yes"

        try:
            model.CalculateStatics()
            results["tests"].append({"component": f"Line: {line.name}", "passed": True})
        except Exception as e:
            results["tests"].append({
                "component": f"Line: {line.name}",
                "passed": False,
                "error": str(e)
            })
            results["failing_component"] = line.name

            # Disable this line and continue
            line.IncludedInStatics = "No"

    return results
```


## Solver Settings Adjustment


```python
def adjust_solver_for_convergence(model) -> bool:
    """
    Progressively adjust solver settings to achieve convergence.

    Returns True if convergence achieved.
    """
    # Settings to try
    damping_values = [10, 20, 50, 100, 200]
    tolerance_values = [1e-5, 1e-4, 1e-3, 1e-2]

    for damping in damping_values:
        for tolerance in tolerance_values:
            try:
                # Apply settings
                model.general.StaticsDamping = damping
                model.general.StaticsTolerance = tolerance

                # Try statics
                model.CalculateStatics()
                print(f"Converged with Damping={damping}, Tolerance={tolerance}")
                return True

            except OrcFxAPI.OrcaFlexError:
                continue

    print("Failed to converge with any settings combination")
    return False
```
