---
name: openfoam-31-solver-log-residual-format
description: 'Sub-skill of openfoam: 3.1 Solver Log Residual Format (+5).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# 3.1 Solver Log Residual Format (+5)

## 3.1 Solver Log Residual Format


Each iteration produces lines in this format:
```
smoothSolver:  Solving for Ux, Initial residual = 0.0118755, Final residual = 0.000302581, No Iterations 1
GAMG:  Solving for p, Initial residual = 0.150883, Final residual = 0.00896498, No Iterations 3
```

**Regex for extraction:**
```python
import re
pattern = r'^(\w+):\s+Solving for (\w+), Initial residual = ([0-9.e+-]+), Final residual = ([0-9.e+-]+), No Iterations (\d+)'
# Groups: solver_name, field_name, initial_residual, final_residual, iterations
```

**Time step markers:**
```
Time = 150                    # steady: iteration number
Time = 0.0345                 # transient: physical time
```

**Courant number (transient only):**
```
Courant Number mean: 0.123 max: 0.987
```

**Continuity errors:**
```
time step continuity errors : sum local = 1.23e-07, global = -2.34e-15, cumulative = -5.67e-14
```

**Convergence marker (SIMPLE):**
```
SIMPLE solution converged in 285 iterations
```

**End marker:** `End`


## 3.2 foamLog Utility


```bash
foamLog log.simpleFoam
# Creates logs/ directory with per-field residual files:
#   logs/p_0          — initial residual for p
#   logs/Ux_0         — initial residual for Ux
#   logs/k_0          — initial residual for k
#   logs/contLocal_0  — local continuity error
#   logs/contGlobal_0 — global continuity error
# Format: two columns (iteration, value)
```


## 3.3 Python Log Parsing


```python
import re
from pathlib import Path

def parse_openfoam_log(log_path):
    """Parse OpenFOAM solver log and extract residuals per field."""
    residuals = {}
    time_step = 0
    pattern = re.compile(
        r'(\w+):\s+Solving for (\w+), '
        r'Initial residual = ([0-9.e+-]+), '
        r'Final residual = ([0-9.e+-]+), '
        r'No Iterations (\d+)'
    )
    time_pattern = re.compile(r'^Time = ([0-9.e+-]+)')

    for line in Path(log_path).read_text().splitlines():
        time_match = time_pattern.match(line)
        if time_match:
            time_step = float(time_match.group(1))
            continue
        match = pattern.search(line)
        if match:
            field = match.group(2)
            if field not in residuals:
                residuals[field] = []
            residuals[field].append({
                'time': time_step,
                'initial': float(match.group(3)),
                'final': float(match.group(4)),
                'iterations': int(match.group(5)),
            })
    return residuals
```


## 3.4 postProcessing/ Directory


Function objects write to `postProcessing/<name>/<startTime>/`:

| Function Object | Output File | Content |
|-----------------|-------------|---------|
| `yPlus` | `yPlus/0/yPlus.dat` | Wall y+ values |
| `solverInfo` | `solverInfo/0/solverInfo.dat` | Residuals per timestep |
| `forceCoeffs` | `forceCoeffs/0/coefficient.dat` | Cd, Cl, Cm vs time |
| `probes` | `probes/0/p`, `probes/0/U` | Field values at probe points |
| `fieldMinMax` | `fieldMinMax/0/fieldMinMax.dat` | Min/max per field |


## 3.5 checkMesh Output


Key lines to parse:
```
Max aspect ratio = 5.08 OK.
Mesh non-orthogonality Max: 45.2 average: 12.3
Max skewness = 0.127 OK.
Min volume = 4.2e-11. Max volume = 1.68e-09.
Mesh OK.                                    # or: Failed N mesh checks.
```


## 3.6 Exit Codes


| Code | Meaning |
|------|---------|
| 0 | Success (`End` printed) |
| 1 | FOAM FATAL ERROR or FOAM FATAL IO ERROR |
| 134 | SIGABRT — assertion failure |
| 136 | SIGFPE — floating point exception |
| 139 | SIGSEGV — memory / corrupted mesh |
| 137 | SIGKILL — out of memory (OOM killer) |
| 255 | MPI error / decomposition mismatch |

---
