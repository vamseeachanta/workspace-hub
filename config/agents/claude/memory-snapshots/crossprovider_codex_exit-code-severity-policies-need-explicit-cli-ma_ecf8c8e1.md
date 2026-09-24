---
name: crossprovider codex exit-code-severity-policies-need-explicit-cli-ma
description: Exit-code/severity policies need explicit CLI mapping
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [CLI-design, exit-codes, user-control]
---

Policies stating "PASS/WARN/FAIL for X condition" must map to user-facing CLI options (e.g., `--require-license`, `--require-executable`) to be implementable and testable. Exit-code policy without CLI surface is not actionable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
