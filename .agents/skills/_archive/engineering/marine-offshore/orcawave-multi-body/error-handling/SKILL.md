---
name: orcawave-multi-body-error-handling
description: 'Sub-skill of orcawave-multi-body: Error Handling.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


```python
# Handle multi-body analysis errors
try:
    mb = MultiBodyAnalysis()
    mb.add_body("FPSO", "fpso.gdf", [0, 0, 0])
    mb.add_body("Tanker", "tanker.gdf", [280, 15, 0])
    results = mb.run()

except MeshOverlapError as e:
    print(f"Bodies overlap: {e}")
    # Adjust body positions

except GapTooNarrowError as e:
    print(f"Gap too narrow for reliable results: {e}")
    # Minimum gap typically 2m

except CouplingConvergenceError as e:
    print(f"Coupling calculation did not converge: {e}")
    # Reduce frequency range or check mesh quality
```
