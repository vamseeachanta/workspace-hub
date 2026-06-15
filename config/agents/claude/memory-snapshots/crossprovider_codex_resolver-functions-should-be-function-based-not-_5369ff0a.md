---
name: crossprovider codex resolver-functions-should-be-function-based-not-
description: Resolver functions should be function-based, not source-time exits
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [shell, functions, environment-setup, patterns]
---

Environment resolver patterns (finding and validating tool paths like 'uv' for shell callers) should return values via function calls, not exit at source time. Function-based patterns remain compatible with diverse calling contexts (direct sourcing, subshells, error traps), while source-time exits break calling code unexpectedly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
