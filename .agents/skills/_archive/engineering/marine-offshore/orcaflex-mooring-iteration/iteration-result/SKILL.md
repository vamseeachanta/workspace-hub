---
name: orcaflex-mooring-iteration-iteration-result
description: 'Sub-skill of orcaflex-mooring-iteration: Iteration Result (+1).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Iteration Result (+1)

## Iteration Result


```python
@dataclass
class IterationResult:
    converged: bool               # Did iteration succeed?
    iterations: int               # Number of iterations
    final_tensions: Dict[str, float]  # Final tensions per line
    final_lengths: Dict[str, List[float]]  # Final section lengths
    max_error: float              # Final maximum error %
    execution_time: float         # Total time in seconds
    convergence_history: List[float]  # Error at each iteration
```

## Report Format


```
================================================================================
MOORING TENSION ITERATION REPORT
================================================================================

Configuration:
  Method: scipy
  Max Iterations: 50
  Tolerance: 1.0%
  Damping Factor: 0.7

*See sub-skills for full details.*
