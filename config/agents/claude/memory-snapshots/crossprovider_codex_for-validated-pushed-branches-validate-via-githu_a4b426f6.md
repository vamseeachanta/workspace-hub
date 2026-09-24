---
name: crossprovider codex for-validated-pushed-branches-validate-via-githu
description: For validated pushed branches, validate via GitHub API instead of local Git
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow, validation, performance, github-api]
---

When a branch already has prior implementation and validation evidence (commits, PR checks, prior comments), shift to GitHub's structured API and PR/CI data rather than running broad local `git status/log/diff` in saturated worktrees. Avoids blocking the lane and provides authoritative state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
