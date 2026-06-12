---
name: crossprovider codex branches-may-be-local-only-in-worktree-not-visib
description: Branches may be local-only in worktree, not visible on GitHub
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [branch-visibility, worktree-isolation]
---

Issue execution branches created in isolated worktrees (e.g., `issue-2747-ledger-codex`) may not be pushed to GitHub and remain invisible to GitHub connector search/compare endpoints. Always verify branch existence before attempting connector reads; if local-only, fall back to worktree file inspection if local shell permits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
