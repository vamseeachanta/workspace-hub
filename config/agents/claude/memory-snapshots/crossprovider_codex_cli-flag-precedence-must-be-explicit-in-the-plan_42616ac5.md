---
name: crossprovider codex cli-flag-precedence-must-be-explicit-in-the-plan
description: CLI flag precedence must be explicit in the plan and tested, not assumed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cli-design, flag-semantics, test-coverage]
---

When a command-line tool has multiple flags that interact (e.g., --ruff-only, --mypy-only, --docs), document the precedence rule clearly in the spec and include tests for combinations. Implicit assumptions lead to implementation drift and reviewer confusion (e.g., does --ruff-only suppress ruff, or everything?).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
