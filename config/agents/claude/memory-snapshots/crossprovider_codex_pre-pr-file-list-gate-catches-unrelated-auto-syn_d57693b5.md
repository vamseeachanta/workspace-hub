---
name: crossprovider codex pre-pr-file-list-gate-catches-unrelated-auto-syn
description: Pre-PR file-list gate catches unrelated auto-sync contamination
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [git, auto-sync, pr-workflow, safety-gate]
---

Auto-sync sweeps unrelated files (251+ observed) from dirty worktree into PRs when checked out on any branch. Require `git diff --name-only origin/main...HEAD` verification before `gh pr create`. If unexpected files appear, stop and report before opening the PR.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
