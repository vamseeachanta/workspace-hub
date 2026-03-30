---
name: orcawave-damping-sweep-error-handling
description: 'Sub-skill of orcawave-damping-sweep: Error Handling.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


```python
# Handle damping analysis errors
try:
    sweep = DampingSweep()
    sweep.load_model("models/fpso.owr")
    results = sweep.run(parameter="roll_damping", values=[0.05, 0.10])

except DampingOutOfRangeError as e:
    print(f"Damping value unrealistic: {e}")
    # Typical range 1-20% critical

except NegativeDampingError as e:
    print(f"Negative damping detected: {e}")
    # Check model setup

except ConvergenceError as e:
    print(f"Analysis did not converge: {e}")
    # Reduce damping or check mesh
```
