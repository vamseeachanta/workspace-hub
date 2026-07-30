---
name: crossprovider codex changed-yaml-config-files-must-be-explicitly-gat
description: Changed YAML config files must be explicitly gated by format/lint hooks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [config, verification-gates, yaml, linting]
---

Scheduler config changes need explicit gates (e.g., `check-yaml`, `yamllint` in pre-commit). Plans often miss YAML files in Black/isort format lists because they assume pytest covers all touched surfaces; it doesn't. Name config files explicitly in verification gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
