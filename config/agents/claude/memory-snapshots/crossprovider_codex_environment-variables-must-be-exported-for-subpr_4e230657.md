---
name: crossprovider codex environment-variables-must-be-exported-for-subpr
description: Environment variables must be exported for subprocess access
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [subprocess, environment-variables, python, shell-integration]
---

When Python code reads `os.environ["VAR"]`, a shell variable assignment alone does not propagate the value. The variable must be explicitly exported (`export VAR=...`) before the Python process runs, or it will raise KeyError. This is subtle in workflows that mix shell and Python.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
