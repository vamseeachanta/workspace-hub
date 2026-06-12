---
name: crossprovider codex timeout-command-unavailable-on-macos-in-shell-sc
description: Timeout command unavailable on macOS in shell scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cross-platform, macos, shell-scripting]
---

GNU coreutils `timeout` is not available on macOS by default. Scripts that rely on `timeout` for subprocess limits will hang on macOS. Use perl-based fallback: `perl -e 'alarm(N); system(cmd)'` or conditional check for `timeout` availability with fallback behavior. Cross-platform robustness pattern for orchestration scripts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
