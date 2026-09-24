---
name: crossprovider codex solver-completion-requires-semantic-validation-n
description: Solver completion requires semantic validation, not exit code
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [solver-validation, testing-methodology, CFD, anti-pattern]
---

Exit code zero and positive timestep count do not prove a solver completed requested work; validation requires explicit completion markers (text inspection, output field presence, or parsed results).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
