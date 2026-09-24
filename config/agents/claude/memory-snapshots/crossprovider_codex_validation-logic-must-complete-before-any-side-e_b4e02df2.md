---
name: crossprovider codex validation-logic-must-complete-before-any-side-e
description: Validation logic must complete before any side effects (mkdir, write, etc.)
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation-ordering, fail-closed-design, side-effects]
---

Fail-closed validation gates must run to completion—including exact membership checks, uniqueness, and identity verification—before output directories are created or artifacts written. Side effects during partial validation mean failed checks leave residue and mask the failure mode. Validate all inputs, then execute all writes as a separate phase.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
