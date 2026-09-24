---
name: crossprovider codex remote-command-construction-must-use-safe-templa
description: Remote command construction must use safe templating and quote paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [command-injection, remote-dispatch, shell-safety]
---

Passing remote shell commands through `str.format` breaks with brace expansion, awk, jq, or Python literals. Unquoted paths with spaces or shell metacharacters alter the command. Use safe templating (replace only explicit tokens like `{host}` / `{ranks}`), or relay via environment variables. Always quote `repo_dir` and similar paths in remote invocations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
