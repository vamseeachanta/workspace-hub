---
name: solver-benchmark-solver-paths
description: 'Sub-skill of solver-benchmark: Solver Paths.'
version: 2.0.0
category: engineering-utilities
type: reference
scripts_exempt: true
---

# Solver Paths

## Solver Paths


Configure solver paths in the script or via environment variables:

```python
# In run_3way_benchmark.py
SOLVER_PATHS = {
    "orcawave": None,  # Uses OrcFxAPI
    "aqwa": Path("C:/Program Files/ANSYS Inc/v252/aqwa/bin/winx64/Aqwa.exe"),
    "bemrosetta": Path("D:/software/BEMRosetta/BEMRosetta_cl.exe"),
}
```

*See sub-skills for full details.*
