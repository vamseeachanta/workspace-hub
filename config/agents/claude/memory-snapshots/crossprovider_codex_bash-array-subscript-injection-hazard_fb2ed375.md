---
name: crossprovider codex bash-array-subscript-injection-hazard
description: Bash array subscript injection hazard
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [bash, security, shell-injection]
---

Associative array subscripts in bash perform expansions; unvalidated input from files or user input can trigger code injection. Always validate array keys before lookup (e.g., `[[ $key =~ ^[A-Z0-9-]+$ ]]`) or use alternative data structures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
