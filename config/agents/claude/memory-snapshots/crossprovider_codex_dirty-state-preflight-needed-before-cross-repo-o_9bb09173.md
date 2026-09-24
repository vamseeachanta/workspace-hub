---
name: crossprovider codex dirty-state-preflight-needed-before-cross-repo-o
description: Dirty-state preflight needed before cross-repo operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, sibling-repos, operational-gates]
---

Before operating across sibling repos, enumerate expected repos from registry and verify each has clean git state with NUL-safe git status check; no auto-stash or unexpected-state tolerance. This prevents sibling mutations cascading from one repo to others.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
