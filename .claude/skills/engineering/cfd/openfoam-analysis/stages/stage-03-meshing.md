# Stage 3: Meshing

> CFD-specific stage — no direct calc-methodology mapping

## Entry

- Case directory from Stage 2
- Geometry definition from analysis YAML

## Mesh Methods

### blockMesh (simple geometries)
```bash
source /usr/lib/openfoam/openfoam2312/etc/bashrc 2>/dev/null || true
cd <case_dir>
blockMesh > log.blockMesh 2>&1
checkMesh > log.checkMesh 2>&1
```

### gmsh → OpenFOAM (complex geometries)
```bash
# Generate mesh with gmsh (refer to gmsh-meshing skill)
gmsh -3 geometry.geo -o mesh.msh -format msh22
# Convert to OpenFOAM
gmshToFoam mesh.msh
checkMesh > log.checkMesh 2>&1
```

### snappyHexMesh (STL-based)
```bash
# Place STL in constant/triSurface/
surfaceFeatureExtract
blockMesh                    # background mesh
snappyHexMesh -overwrite
checkMesh > log.checkMesh 2>&1
```

## Quality Gate (automated — script parses checkMesh output)

```python
import re
from pathlib import Path

def check_mesh_quality(log_path):
    """Parse checkMesh log, return pass/fail verdict."""
    text = Path(log_path).read_text()
    verdict = {"pass": True, "issues": []}
    
    checks = [
        (r"Max aspect ratio = ([0-9.e+-]+)", 100, "aspect_ratio"),
        (r"Max skewness = ([0-9.e+-]+)", 4, "skewness"),
        (r"Mesh non-orthogonality Max: ([0-9.e+-]+)", 70, "non_orthogonality"),
    ]
    for pattern, limit, name in checks:
        m = re.search(pattern, text)
        if m and float(m.group(1)) > limit:
            verdict["pass"] = False
            verdict["issues"].append(f"{name}={m.group(1)} exceeds {limit}")
    
    if "negative" in text.lower() and "volume" in text.lower():
        verdict["pass"] = False
        verdict["issues"].append("negative_volumes_detected")
    
    return verdict
```

## Exit Gate

- [ ] `checkMesh` reports "Mesh OK" (or all metrics within thresholds)
- [ ] No negative volumes
- [ ] Cell count within target range (±50% of analysis YAML target)
- [ ] Mesh quality verdict written to `<case>/mesh-verdict.yaml`
