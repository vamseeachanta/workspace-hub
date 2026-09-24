---
name: crossprovider codex shell-scripts-emitting-user-commands-must-quote-
description: Shell scripts emitting user commands must quote paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell, command-emission, escaping]
---

When emitting broker/git commands for operators to paste and run, use `printf %q` or shell quoting on all paths and arguments. Unquoted paths with spaces or metacharacters produce broken or unsafe commands.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
