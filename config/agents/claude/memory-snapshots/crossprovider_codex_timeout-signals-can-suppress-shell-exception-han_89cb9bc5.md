---
name: crossprovider codex timeout-signals-can-suppress-shell-exception-han
description: Timeout signals can suppress shell exception handlers
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [timeout-handling, signal-safety, shell-scripting, error-markers]
---

When a subprocess timeout kills a process (SIGTERM/SIGKILL), Python exception handlers may not run to emit expected markers. Shell wrappers around bounded subprocesses must include fallback emit logic that fires even on signal termination, not just normal error paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
