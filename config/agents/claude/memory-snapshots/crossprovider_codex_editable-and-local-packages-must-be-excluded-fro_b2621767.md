---
name: crossprovider codex editable-and-local-packages-must-be-excluded-fro
description: Editable and local packages must be excluded from third-party vulnerability audits
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [dependency-management, python-tooling]
---

Exports from projects with `tool.uv.sources` (workspace members, local paths) include `-e .` entries that break third-party scanners. Use `--no-editable` flag when exporting for audit to produce clean pinned third-party dependencies only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
