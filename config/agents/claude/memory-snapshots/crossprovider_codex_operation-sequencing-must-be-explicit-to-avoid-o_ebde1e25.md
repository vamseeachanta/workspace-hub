---
name: crossprovider codex operation-sequencing-must-be-explicit-to-avoid-o
description: Operation sequencing must be explicit to avoid overwrites
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, operations, sequencing]
---

When operations interact with prior state (e.g., regenerating audit results, re-running analyses), the sequence of operations must be unambiguous. Prior-audit delta sequencing or prior-state handling must be documented at the plan level to prevent overwrite ambiguity during execution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
