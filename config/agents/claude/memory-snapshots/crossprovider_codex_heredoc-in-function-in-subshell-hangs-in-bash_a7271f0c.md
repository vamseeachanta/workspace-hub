---
name: crossprovider codex heredoc-in-function-in-subshell-hangs-in-bash
description: Heredoc-in-function-in-subshell hangs in bash
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, subshells, debugging, gotcha]
---

Avoid constructing heredocs inside functions that are called in subshells—causes hangs. Workaround: write helper script to mktemp file before execution, execute with explicit path, trap cleanup. Applies to Python/shell helpers in pipelines.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
