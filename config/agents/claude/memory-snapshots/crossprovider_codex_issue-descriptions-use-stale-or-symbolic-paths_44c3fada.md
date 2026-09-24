---
name: crossprovider codex issue-descriptions-use-stale-or-symbolic-paths
description: Issue descriptions use stale or symbolic paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [issue-tracking, path-verification, repo-state]
---

GitHub issue descriptions often reference old paths (e.g., `knowledge/wikis/` when actual repo uses `wikis/...`). Cross-check issue paths against current repo layout before executing any implementation. Existing plan artifacts often already capture the corrected paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
