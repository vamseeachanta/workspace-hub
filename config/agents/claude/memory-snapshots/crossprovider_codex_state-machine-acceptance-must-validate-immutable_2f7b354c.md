---
name: crossprovider codex state-machine-acceptance-must-validate-immutable
description: State machine acceptance must validate immutable proofs before appending terminal records
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [state-machine-design, acceptance-criteria, validation-ordering]
---

State transitions to terminal states (ACCEPTED, PUBLISHED) should require the caller to present validated immutable proofs, and the writer should reject malformed/skipped journals. If the append operation is presented as directly callable without prior validation, it enables operational bypasses. Require full prior-state history validation before any terminal-state record is written.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
