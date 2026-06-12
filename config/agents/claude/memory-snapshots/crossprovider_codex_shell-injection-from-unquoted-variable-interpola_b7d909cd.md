---
name: crossprovider codex shell-injection-from-unquoted-variable-interpola
description: Shell injection from unquoted variable interpolation in commands
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-safety, injection, work.sh, WRK-118]
---

Passing user input or dynamic strings to `bash -c "... $var ..."` without quoting breaks on special characters like apostrophes. WRK-118 work.sh:50 interpolates WRK title directly: `bash -c "... classify_task '$_title'"` fails on titles like "Bob's refactor". Use safe patterns: pass as positional params to subshell, or source classifier in-process and call directly with proper quoting.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
