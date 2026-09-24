---
name: crossprovider codex non-blocking-passes-must-surface-tool-failures-d
description: Non-blocking passes must surface tool failures distinctly
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, error-handling, shell-scripts]
---

When a process is non-blocking for findings, still distinguish tool failure (config error, import failure) from 'no new findings'. Use temp files, JSON validation, and explicit stderr output so developers know the scan actually ran. Silent failures hide coverage gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
