---
name: crossprovider codex codex-multi-repo-workspaces-use-purpose-built-js
description: Codex + multi-repo workspaces: use purpose-built JSON drivers, avoid raw git probes
metadata:
  type: reference
  source: codex
  bridged: 2026-07-09
  tags: [codex, repo-hygiene, performance-pattern]
---

Large workspaces with many repos/worktrees cause `git status`, `git diff`, and broad filesystem scans to hang or produce excessive noise. Instead, use shell drivers that emit JSON (e.g., `reconcile-ecosystem.sh`), then filter locally with `jq`. Keeps context bounded and avoids noisy untracked traversal.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
