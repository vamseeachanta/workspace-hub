---
name: crossprovider codex pre-existing-legal-lint-violations-should-be-dis
description: Pre-existing legal/lint violations should be disclosed and not silently inherited by task scope
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [review-discipline, scope-management, reporting]
---

When a broad scan (e.g., full-repo legal check, Ruff linting) contains pre-existing violations outside the task scope, document the count and nature separately. Do not mark the task as FAILED due to unrelated violations; instead explicitly record 'Task paths pass, unrelated pre-existing violations: N'.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
