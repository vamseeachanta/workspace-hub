---
name: crossprovider codex generic-error-suppression-2-dev-null-true-masks-
description: Generic error suppression (2>/dev/null || true) masks real failures; use per-error remediation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, shell-scripting, audit-design]
---

WRK-1016 proposed blanket hook error suppression as performance fix; this masks real hook failures while appearing to succeed. Make explicit per-error decisions (is error expected? is hook optional? fail-safe or fail-loud?) instead of blanket suppression.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
