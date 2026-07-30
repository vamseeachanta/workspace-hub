---
name: crossprovider codex status-must-be-deterministically-derived-never-a
description: Status must be deterministically derived, never authored
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [state-management, determinism]
---

If status can be manually edited, drift is silent and undetectable. Use a closed enum derived from actual state; forbid authored status fields to prevent unobservable divergence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
