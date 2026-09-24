---
name: crossprovider codex exit-code-semantics-are-tool-specific-ports-must
description: Exit-code semantics are tool-specific; ports must account for tool behavior
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tool-semantics, exit-codes, tool-porting, scripting-contracts]
---

When porting a fix pattern between similar tools (e.g., ruff ratcheting to mypy), exit-code meanings differ significantly. Mypy: 2=crash/usage-error, 1=type-errors, 0=clean. A port cannot just mirror structure; it must account for tool-specific exit semantics, especially around fail-open behavior and ratchet logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
