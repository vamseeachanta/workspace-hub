---
name: crossprovider codex shell-to-language-bridges-must-use-safe-argument
description: Shell-to-language bridges must use safe argument passing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, security, python, cli]
---

String interpolation of user input into here-doc Python code is an injection vector. Pass user arguments via environment variables or `sys.argv` instead, and validate expected types (e.g., integers) before use.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
