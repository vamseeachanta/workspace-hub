---
name: crossprovider codex repo-wide-searches-over-large-generated-datasets
description: Repo-wide searches over large generated datasets cause slow audits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [llm-wiki, repo-audit, performance]
---

Searching with regex over `wikis/` or large extracted source bodies hits multi-MB datasets and causes audits to stall. Scope searches to `scripts/`, `tests/`, `docs/plans/`, and specific `data/document-index/` artifacts instead. Use `rg --files` with targeted root paths rather than broad `find` commands.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
