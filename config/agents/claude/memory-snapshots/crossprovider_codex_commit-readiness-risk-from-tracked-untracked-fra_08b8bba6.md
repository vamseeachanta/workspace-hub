---
name: crossprovider codex commit-readiness-risk-from-tracked-untracked-fra
description: Commit-readiness risk from tracked/untracked fragmentation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, commit-readiness, artifact-tracking]
---

When index/log entries (tracked) reference new pages or artifacts (untracked), `git diff` shows only the tracked changes. A normal pathspec commit omitting untracked files ships dangling index references. Always verify `git status --untracked-files=all` shows zero new artifacts, or explicitly include them in the commit command.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
