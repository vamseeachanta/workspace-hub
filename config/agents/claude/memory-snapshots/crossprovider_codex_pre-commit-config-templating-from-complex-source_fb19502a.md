---
name: crossprovider codex pre-commit-config-templating-from-complex-source
description: Pre-commit config templating from complex source repos introduces risk—use minimal snippets instead
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pre-commit, configuration-management, risk-mitigation]
---

Copying a full `.pre-commit-config.yaml` from a repo with many non-ruff hooks (e.g., digitalmodel) into target repos will propagate unrelated, repo-specific entries. Define a minimal ruff-only snippet for new repos; let target repos add their own hooks intentionally.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
