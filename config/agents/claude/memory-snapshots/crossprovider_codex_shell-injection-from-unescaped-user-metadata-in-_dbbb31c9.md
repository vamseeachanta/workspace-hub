---
name: crossprovider codex shell-injection-from-unescaped-user-metadata-in-
description: Shell injection from unescaped user metadata in task-routed commands
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, shell-scripting, injection, workflow]
---

WRK-118 found title-based routing vulnerable via unescaped WRK title in `bash -c` string; e.g., "Bob's refactor" breaks parsing. Any user-facing metadata (WRK title, description, config values) flowing into shell commands must avoid string interpolation — use positional args or source files instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
