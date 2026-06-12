---
name: crossprovider codex set-e-traps-on-arithmetic-operations-use-true-id
description: set -e traps on arithmetic operations; use || true idiom
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [bash-patterns, error-handling, set-e]
---

In bash scripts with `set -e`, constructs like `(( valid++ ))` can terminate the script on first increment if the result evaluates to zero in certain edge cases. Use `(( valid++ )) || true` or avoid arithmetic as statement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
