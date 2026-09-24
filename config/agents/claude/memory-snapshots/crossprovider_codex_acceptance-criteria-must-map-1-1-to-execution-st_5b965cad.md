---
name: crossprovider codex acceptance-criteria-must-map-1-1-to-execution-st
description: Acceptance criteria must map 1:1 to execution steps; unmapped ACs = gate failure
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, acceptance-criteria, specification]
---

WRK-1016 AC 'audit all settings files' but execution only covered .claude/settings.json, missing .pre-commit-config.yaml, uv.toml, etc. WRK-1053 AC 'category-based audit' but implementation did script-reference audit instead. Before approval, verify each AC has ≥1 execution step; gaps block gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
