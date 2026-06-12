---
name: crossprovider hermes validator-gate-ordering-verify-before-execute-no
description: Validator gate ordering: verify before execute, not after
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validator-design, control-flow, acceptance-criteria]
---

Version validation gates that run after expensive operations (solver, tutorials, or heavy compute) violate the gatekeeper contract—wrong version can still consume time and mask root causes. Gates must verify canonical runtime before invoking delegated work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
