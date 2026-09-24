---
name: crossprovider codex orphaned-infrastructure-from-migrations-accumula
description: Orphaned infrastructure from migrations accumulates systematically
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migration, maintenance, ci-health]
---

When code is deleted (e.g., scripts/agents/ directory), CI config and pre-commit hooks that reference it remain dangling. Review CI/hook files against script inventory during cleanup; missing targets block CI unless config is updated or scripts are restored.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
