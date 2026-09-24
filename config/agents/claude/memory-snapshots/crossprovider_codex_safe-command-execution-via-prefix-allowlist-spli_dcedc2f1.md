---
name: crossprovider codex safe-command-execution-via-prefix-allowlist-spli
description: Safe command execution via prefix allowlist + split() instead of shell=True
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, command-injection, subprocess, defense-in-depth]
---

Prevent command injection in tools that execute user-provided commands by: (1) maintaining a safe-prefix allowlist (e.g., 'uv ', 'python', 'git '), (2) an unsafe-pattern regex (e.g., 'rm -[rf]', '> /'), and (3) using subprocess.run(cmd.split()) with NO shell=True. Requires exact prefix matching and safe patterns as the first layer.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
