---
name: gmsh-openfoam-orcaflex-quick-invocation
description: 'Sub-skill of gmsh-openfoam-orcaflex: Quick Invocation.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Quick Invocation

## Quick Invocation


```bash
# Real mode (all three solvers installed)
python3 scripts/pipelines/gmsh_openfoam_orcaflex.py \
    --diameter 1.0 --length 5.0 --velocity 1.5 \
    --work-dir /tmp/pipeline_run

# Stub mode (no solver licenses required — CI / dev-primary)
python3 scripts/pipelines/gmsh_openfoam_orcaflex.py \
    --diameter 1.0 --length 5.0 --velocity 1.5 \
    --work-dir /tmp/pipeline_run --stub-mode

# Shell wrapper
bash scripts/pipelines/gmsh_openfoam_orcaflex.sh \
    --diameter 1.0 --length 5.0 --velocity 1.5 --stub-mode

# Run full test suite (no solvers required)
cd scripts/pipelines && python3 -m pytest test_cylinder_in_flow.py -v
```
