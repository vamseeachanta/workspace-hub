---
name: crossprovider codex pre-commit-hook-yaml-indentation-errors-break-si
description: Pre-commit hook YAML indentation errors break silently
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pre-commit, yaml, configuration, validation]
---

Invalid YAML indentation in `.pre-commit-config.yaml` (e.g., hook repo entry not nested under 'repos:' list) breaks pre-commit loading with obscure or silent failures. Always validate pre-commit config syntax with `pre-commit validate-manifest` after edits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
