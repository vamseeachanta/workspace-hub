---
name: crossprovider codex large-cli-context-argument-exceeds-os-arg-max-li
description: Large CLI context argument exceeds OS ARG_MAX limit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell, limits, cli, performance]
---

Passing multi-kilobyte prompt context as a single command-line argument exceeds typical ARG_MAX (~128KB on many systems). Use temp files or stdin redirection instead to avoid silent truncation or failure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
