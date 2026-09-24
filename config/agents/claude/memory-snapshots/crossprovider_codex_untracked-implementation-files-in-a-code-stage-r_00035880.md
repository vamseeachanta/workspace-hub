---
name: crossprovider codex untracked-implementation-files-in-a-code-stage-r
description: Untracked implementation files in a code-stage review block the review gate
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, git-discipline, traceability, release-management]
---

When the branch diff is empty because all implementation is untracked, `git diff main...HEAD` shows no changes. This is a release-blocking defect in gate discipline — code-stage reviews cannot gate on unstaged/uncommitted artifacts. Verify at planning stage: implementation must be tracked/staged before code-stage reviews begin.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
