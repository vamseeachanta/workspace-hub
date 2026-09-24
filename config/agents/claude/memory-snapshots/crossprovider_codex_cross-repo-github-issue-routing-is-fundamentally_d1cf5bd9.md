---
name: crossprovider codex cross-repo-github-issue-routing-is-fundamentally
description: Cross-repo GitHub issue routing is fundamentally limited by design
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-repo, routing-architecture, github-integration]
---

Current kanban/dispatch designs bind issues to their source repository (via `issue_key()`) and only support repo-internal domain placement. Transferring issues across repos requires explicit routing models or issue recreation; label-based routing alone cannot bridge repos.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
