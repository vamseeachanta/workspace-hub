---
name: crossprovider codex gpu-claw-deployment-uses-established-deckhand-op
description: GPU-claw deployment uses established Deckhand openfoam-run-batch method
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [gpu-dispatch, deployment-pattern, deckhand]
---

Work targeting gpu-claw should use the Deckhand `openfoam-run-batch` method (request/claim/work-directory/artifact-return/retry contracts), not direct SSH or local execution. This is the canonical deployment path verified in prior Claude sessions; it must be fixed into plans and method references.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
