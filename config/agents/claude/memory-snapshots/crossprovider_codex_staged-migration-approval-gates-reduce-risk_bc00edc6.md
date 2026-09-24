---
name: crossprovider codex staged-migration-approval-gates-reduce-risk
description: Staged migration approval gates reduce risk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, migration-pattern, approval-gates]
---

Multi-phase migrations benefit from separate approval checkpoints: APPROVED_FOR_DRYRUN (manifest validation), APPROVED_FOR_SIMULATION (fail-fast checks), APPROVED (actual apply). Single all-or-nothing approval doesn't catch issues discovered during early phases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
