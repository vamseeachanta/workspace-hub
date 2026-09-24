---
name: crossprovider codex conditional-fallback-strategy-exit-code-contract
description: Conditional fallback strategy: exit code contracts prevent silent failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [error-handling, codex, orchestration, contracts]
---

Enforce hard-gated exit code contracts before applying fallback behavior (e.g., NO_OUTPUT handler only for genuine codex exit 0/5, not 1/2/other). Prevents misclassified failures from triggering wrong fallbacks and masking real errors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
