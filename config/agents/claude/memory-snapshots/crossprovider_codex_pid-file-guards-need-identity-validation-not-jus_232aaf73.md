---
name: crossprovider codex pid-file-guards-need-identity-validation-not-jus
description: PID file guards need identity validation, not just existence checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [process-safety, pid-management, hotkey-launchers]
---

Checking `kill -0 $pid` to guard process stopping is insufficient; stale PID files or reused process IDs can kill unrelated processes. Validate `/proc/$pid/cmdline` and metadata (start time, expected binary, target file) before killing. Regression tests that pass when unrelated processes are killed are unsafe — verify the specific expected process was stopped.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
