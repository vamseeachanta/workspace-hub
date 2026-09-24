---
name: crossprovider codex tool-scopes-must-be-consistent-across-linters-an
description: Tool scopes must be consistent across linters and type checkers; allowlist non-src Python files explicitly
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-repo-tooling, configuration-consistency, false-positives, WRK-1056]
---

When running multiple tools (ruff, mypy) across tier-1 repos, define identical target sets (e.g., `src tests`) so results are consistent. Legitimate Python files outside src/ (examples/, build/, templates/) will create false failures unless the allowlist is specified upfront. Use --exclude or define tool-specific scope rather than letting ruff's default 'check everything' override mypy's 'only src/' scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
