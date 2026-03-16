---
name: cfd-pipeline-openfoam-case-setup-from-mesh
description: 'Sub-skill of cfd-pipeline: OpenFOAM Case Setup from Mesh (+2).'
version: 1.0.1
category: engineering
type: reference
scripts_exempt: true
---

# OpenFOAM Case Setup from Mesh (+2)

## OpenFOAM Case Setup from Mesh


```bash
# After meshing, set up the solver case:
# 1. Copy 0/ boundary conditions (must match mesh patches)
# 2. Configure system/controlDict
# 3. Configure system/fvSchemes and system/fvSolution
# 4. Set physical properties in constant/

# Check that boundary names in 0/ match polyMesh/boundary
grep -r "type" constant/polyMesh/boundary | grep -v "//"
ls 0/  # Should have U, p, k, omega, etc.
```


## Boundary Condition Consistency Check


```python
def check_bc_consistency(case_dir):
    """Verify boundary conditions match mesh patches."""
    from pathlib import Path
    import re

    # Get mesh patches
    boundary_file = Path(case_dir) / 'constant' / 'polyMesh' / 'boundary'
    boundary_text = boundary_file.read_text()
    mesh_patches = set(re.findall(r'^\s+(\w+)\s*$', boundary_text, re.MULTILINE))

    # Get BC patches from 0/ files
    zero_dir = Path(case_dir) / '0'
    issues = []

    for bc_file in zero_dir.glob('*'):
        if bc_file.is_file():
            content = bc_file.read_text()
            bc_patches = set(re.findall(r'^\s+(\w+)\s*\{', content, re.MULTILINE))

            # Remove non-patch entries
            bc_patches -= {'boundaryField', 'internalField', 'FoamFile', 'dimensions'}

            missing = bc_patches - mesh_patches
            if missing:
                issues.append(f"{bc_file.name}: references non-existent patches: {missing}")

    return issues
```


## Solver Execution


```bash
# Serial execution
simpleFoam -case /path/to/case 2>&1 | tee log.simpleFoam

# Parallel execution
decomposePar -case /path/to/case
mpirun -np 4 simpleFoam -parallel -case /path/to/case 2>&1 | tee log.simpleFoam
reconstructPar -case /path/to/case
```
