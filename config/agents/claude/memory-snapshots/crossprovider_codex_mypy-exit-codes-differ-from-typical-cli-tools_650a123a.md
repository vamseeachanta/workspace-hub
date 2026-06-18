---
name: crossprovider codex mypy-exit-codes-differ-from-typical-cli-tools
description: Mypy exit codes differ from typical CLI tools
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [mypy, exit-codes, quality-gates]
---

mypy exit 2 = crash/usage error (never ratchet), exit 1 = type errors (ratchet-able), exit 0 = clean. This differs from ruff and most tools; handle-all patterns must check exit code before deciding whether to apply baseline comparison or hard-fail.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
