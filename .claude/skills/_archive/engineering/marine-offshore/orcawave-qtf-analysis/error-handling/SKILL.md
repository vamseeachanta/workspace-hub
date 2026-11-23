---
name: orcawave-qtf-analysis-error-handling
description: 'Sub-skill of orcawave-qtf-analysis: Error Handling.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


```python
# Handle QTF computation errors
try:
    results = qtf.compute()
except InsufficientFrequencyResolutionError as e:
    print(f"Need finer frequency resolution: {e}")
    # Increase frequency count
    qtf.configure(frequencies=np.linspace(0.02, 0.5, 50))
    results = qtf.compute()

except HeadingPairError as e:
    print(f"Invalid heading pair configuration: {e}")

except ConvergenceError as e:
    print(f"QTF computation did not converge: {e}")
    # Try different method
    results = qtf.compute(method="control_surface")
```
