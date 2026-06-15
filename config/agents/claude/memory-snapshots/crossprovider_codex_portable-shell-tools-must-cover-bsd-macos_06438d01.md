---
name: crossprovider codex portable-shell-tools-must-cover-bsd-macos
description: Portable shell tools must cover BSD/macOS
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [shell, portability, testing]
---

Scripts claiming portability across machines should not use GNU-only tools (e.g., `date -d` vs POSIX `date`). Add test cases that run on BSD-derivative systems or use `uname` guards. Missing a platform variant silently breaks on that OS.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
