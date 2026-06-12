---
name: crossprovider codex scope-git-add-operations-to-recent-files-to-avoi
description: Scope git add operations to recent files to avoid staging unrelated work
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-safety, file-staging, automation]
---

Using `git add -A .claude/work-queue/pending/` stages ALL matching files, including unrelated drafts from previous operations. For nightly auto-commits, use `find .claude/work-queue/pending/ -name 'WRK-*.md' -mmin -N -exec git add {} +` to scope to files modified in the last N minutes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
