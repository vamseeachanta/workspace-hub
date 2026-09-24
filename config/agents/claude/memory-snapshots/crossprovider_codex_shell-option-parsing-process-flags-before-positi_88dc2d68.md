---
name: crossprovider codex shell-option-parsing-process-flags-before-positi
description: Shell option parsing: process flags before positional arguments
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell, bash, argument-parsing, correctness]
---

When writing shell argument parsers, process option flags (--flag, -f) before positional parameters. Otherwise `script --dry-run WRK-123` misinterprets --dry-run as the positional WRK-ID value.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
