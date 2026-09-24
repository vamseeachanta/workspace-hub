---
name: crossprovider codex repository-layout-changed-cleanup-assumptions-ar
description: Repository layout changed — cleanup assumptions are stale
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, repository-layout, automation, assumptions]
---

Prior cleanup (2026-05-19) reduced root to `workspace-hub/` only, but current layout treats sibling repositories as intentional architecture. Nightly cleanup automation hasn't fired since June (Hermes gateway down), leaving assumptions unapplied. Cleanup registry and worktree-validity heuristics must be updated to reflect live sibling-repo layout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
