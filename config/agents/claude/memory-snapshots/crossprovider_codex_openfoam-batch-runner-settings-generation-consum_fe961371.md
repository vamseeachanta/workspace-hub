---
name: crossprovider codex openfoam-batch-runner-settings-generation-consum
description: OpenFOAM batch runner: settings generation/consumption mismatch
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [openfoam, batch-runner, bug, digitalmodel, cfd]
---

`openfoam_run_batch._render_cases` produces full domain/motion/fill/time/taps settings; `OpenFOAMWorkflow._build_case` consumes only case type/name/solver and drops everything else. Connected-tank geometry and complex BCs cannot reach the runner without fixing this gap.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
