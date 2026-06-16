---
name: crossprovider codex parallel-cleanup-orphans-artifacts-use-git-objec
description: Parallel cleanup orphans artifacts; use git objects as fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [parallel-work, git-objects, artifact-loss, evidence-preservation]
---

When concurrent /tmp cleanup runs in shared repos, file-system evidence (manifests, images) can vanish mid-work. Switch to git object-level inspection (git show, rev-parse) to verify diff content. Worktrees may reappear but their dependencies (manifest CSV, image directories) may not; assume they are gone and plan fallback evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
