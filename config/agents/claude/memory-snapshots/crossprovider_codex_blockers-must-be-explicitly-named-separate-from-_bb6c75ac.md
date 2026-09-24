---
name: crossprovider codex blockers-must-be-explicitly-named-separate-from-
description: Blockers must be explicitly named separate from findings
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-output, clarity, gate-management]
---

Review verdicts should return a distinct 'Blockers' section listing findings that must be resolved before implementation proceeds. This prevents confusion between MAJOR findings that are non-critical and those that actually gate forward progress.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
