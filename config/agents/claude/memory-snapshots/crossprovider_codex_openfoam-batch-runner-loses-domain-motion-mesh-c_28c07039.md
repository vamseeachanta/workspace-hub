---
name: crossprovider codex openfoam-batch-runner-loses-domain-motion-mesh-c
description: OpenFOAM batch runner loses domain/motion/mesh configuration
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [openfoam, workflow, architecture]
---

The `openfoam_run_batch` workflow processes case definitions but `OpenFOAMWorkflow._build_case` drops domain, motion parameters, fill state, prebuilt meshes, and time controls. Advanced multi-body/coupled-geometry cases cannot reach the runner through this path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
