---
name: crossprovider codex scoped-git-operations-with-mtime-filters-prevent
description: Scoped git operations with mtime filters prevent unrelated staging
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-automation, file-scoping, workspace-hygiene]
---

Use `find -mmin N` to limit `git add` to recently-modified files (e.g., files changed in last 2 minutes). Without this scope, a glob pattern like `git add .claude/work-queue/pending/` will stage unrelated human-drafted pending files, silently including them in automated commits. Specificity prevents silent data contamination.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
