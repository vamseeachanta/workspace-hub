---
name: crossprovider codex gate-reviews-must-trace-upstream-dependencies-no
description: Gate reviews must trace upstream dependencies, not just list source files
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [gate-review, planning, upstream-dependencies]
---

Plans that enumerate only direct source files miss runtime dependencies: runner scripts, imported modules, and CI/CD workflow files that the canonical upstream uses. Verify that the implementation traces to exact upstream invocation paths (e.g., which shell calls which Python runner), not just source file inventories.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
