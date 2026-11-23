# Stage 4: Execution

> Maps to calculation-methodology Phase 4 (sections 08-09)

## Entry

- Valid mesh from Stage 3 (mesh-verdict.yaml: pass)

## Run Solver

```bash
source /usr/lib/openfoam/openfoam2312/etc/bashrc 2>/dev/null || true
cd <case_dir>

# Copy 0.orig to 0 if present (standard OpenFOAM pattern)
[[ -d "0.orig" && ! -d "0" ]] && cp -r 0.orig 0

# Serial
<solver> > log.<solver> 2>&1

# Parallel (if decomposeParDict configured)
decomposePar
mpirun -np <N> <solver> -parallel > log.<solver> 2>&1
reconstructPar -latestTime
```

## Convergence Monitoring

The `check-convergence.py` script monitors the solver log in real-time:

```python
import re, sys
from pathlib import Path

def check_convergence(log_path, targets):
    """Check solver convergence from log file.
    
    Returns:
        dict with status (converged|running|diverged), residuals, iterations
    """
    residuals = {}
    pattern = re.compile(
        r'(\w+):\s+Solving for (\w+), '
        r'Initial residual = ([0-9.e+-]+), '
        r'Final residual = ([0-9.e+-]+)'
    )
    
    for line in Path(log_path).read_text().splitlines():
        m = pattern.search(line)
        if m:
            field = m.group(2)
            initial = float(m.group(3))
            residuals[field] = initial
    
    # Check divergence
    for field, value in residuals.items():
        if value > 1e6:
            return {"status": "diverged", "field": field, "residual": value}
    
    # Check convergence
    converged = all(
        residuals.get(f, 1.0) < targets.get(f, 1e-4)
        for f in targets
    )
    
    return {
        "status": "converged" if converged else "running",
        "residuals": residuals,
    }
```

## Early Termination

| Condition | Action |
|-----------|--------|
| Any residual > 1e6 | Stop — diverged, diagnose (see `openfoam` skill §4) |
| Residuals oscillating >500 iterations | Reduce relaxation factors |
| `FOAM FATAL ERROR` in log | Stop — parse error message |
| Convergence target met | Stop — success |

## Exit Gate

- [ ] Solver completed (exit code 0, "End" in log)
- [ ] All residuals below acceptance criteria
- [ ] Continuity errors acceptable (local < 1e-4)
- [ ] No floating point exceptions or fatal errors
- [ ] Convergence verdict written to `<case>/convergence-verdict.yaml`
