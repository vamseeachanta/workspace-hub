---
name: crossprovider codex safe-command-execution-via-allowlist-split-in-me
description: Safe command execution via allowlist + split in memory tooling
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [security, command-execution, injection-prevention, memory-governance]
---

When memory tools optionally check commands, use allowlist prefixes (_SAFE_CMD_PREFIXES like 'uv ', 'git ') + subprocess.run(cmd.split()) without shell=True, blocking unsafe patterns via regex (rm -rf, >, etc). This mitigates injection while preserving auditability for valid commands.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
