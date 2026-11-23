---
name: cfd-pipeline-validation-points-in-the-pipeline
description: 'Sub-skill of cfd-pipeline: Validation Points in the Pipeline (+1).'
version: 1.0.1
category: engineering
type: reference
scripts_exempt: true
---

# Validation Points in the Pipeline (+1)

## Validation Points in the Pipeline


| Stage | What to Check | Tool | Failure Mode |
|-------|--------------|------|--------------|
| **Geometry** | Watertight STL, units (meters) | FreeCAD / meshio | Open surfaces break meshing |
| **Mesh** | checkMesh quality, patch names | OpenFOAM checkMesh | Bad cells cause solver divergence |
| **BCs** | Patches match mesh, physically consistent | Script above | Missing BC crashes solver |
| **Solver** | Residuals converging, Courant < 1 | Log parsing | Divergence = wrong mesh/BCs/schemes |
| **Results** | Value ranges physical, conservation | ParaView validation | Non-physical = wrong setup |
| **Export** | Image non-blank, data non-empty | File size check | Rendering/export config |


## Full Pipeline Validation Script


```python
def validate_cfd_pipeline(case_dir, output_dir):
    """Validate entire CFD pipeline from mesh to results."""
    import subprocess
    import os

    status = {"stages": {}, "overall": True}

    # 1. Mesh quality
    mesh_check = subprocess.run(
        ['checkMesh', '-case', case_dir],
        capture_output=True, text=True
    )
    mesh_ok = 'FAILED' not in mesh_check.stdout
    status["stages"]["mesh"] = {"passed": mesh_ok}
    if not mesh_ok:
        status["overall"] = False

    # 2. Solver completion
    import glob
    time_dirs = [d for d in glob.glob(os.path.join(case_dir, '[0-9]*'))
                 if os.path.isdir(d) and d.split('/')[-1] != '0']
    solver_ok = len(time_dirs) > 0
    status["stages"]["solver"] = {"passed": solver_ok, "time_steps": len(time_dirs)}
    if not solver_ok:
        status["overall"] = False

    # 3. Results physical
    # Check residuals from log
    log_files = glob.glob(os.path.join(case_dir, 'log.*'))
    if log_files:
        import re
        log_text = open(log_files[0]).read()
        final_residuals = re.findall(r'Solving for (\w+).*Final residual = ([\d.e+-]+)', log_text)
        if final_residuals:
            last_residuals = {}
            for name, val in final_residuals:
                last_residuals[name] = float(val)
            converged = all(v < 1e-3 for v in last_residuals.values())
            status["stages"]["convergence"] = {"passed": converged, "residuals": last_residuals}
            if not converged:
                status["overall"] = False

    # 4. Visualization output
    if os.path.isdir(output_dir):
        images = [f for f in os.listdir(output_dir) if f.endswith('.png')]
        viz_ok = len(images) > 0 and all(
            os.path.getsize(os.path.join(output_dir, f)) > 1000 for f in images
        )
        status["stages"]["visualization"] = {"passed": viz_ok, "images": len(images)}

    return status
```
