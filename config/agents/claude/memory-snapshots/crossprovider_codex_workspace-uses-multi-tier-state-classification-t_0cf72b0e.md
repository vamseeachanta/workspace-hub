---
name: crossprovider codex workspace-uses-multi-tier-state-classification-t
description: Workspace uses multi-tier state classification to prevent accidental cleanup of active work
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workspace-management, cleanup-strategy, git-worktrees]
---

Four tiers structure cleanup decisions: Tier 0 (delete), Tier 1 (archive), Tier 2 (reduce in place), Tier 3 (defer/preserve). This prevents accidental removal of registered worktrees, diverged branches, and active concurrent work while enabling systematic management of accumulated state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
