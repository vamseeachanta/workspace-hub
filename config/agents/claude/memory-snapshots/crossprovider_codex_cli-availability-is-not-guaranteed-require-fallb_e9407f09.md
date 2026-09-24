---
name: crossprovider codex cli-availability-is-not-guaranteed-require-fallb
description: CLI availability is not guaranteed; require fallback strategy
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [subprocess, error-handling, dependency-management]
---

Tools like `gemini` CLI, `uv`, or build commands may not be on PATH or may timeout. Always check availability before calling, or catch subprocess errors gracefully. Explicit fallback: carry-forward prior state, skip the feature, or warn and continue. Do not silently fail.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
