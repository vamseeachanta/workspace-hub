---
name: crossprovider codex multi-repo-audit-without-timeouts
description: Multi-repo audit without timeouts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-audit, workspace-health, performance, read-only]
---

Large repos hang on full `git status`; use bounded per-repo commands instead: `git diff --name-only | wc -l` for change counts, `git log --oneline` for local commits, `git symbolic-ref refs/remotes/origin/HEAD` for upstream. Group results into commit-needed, push-needed, clean categories. Timeout repos go into 'manual review' with reproducible commands.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
