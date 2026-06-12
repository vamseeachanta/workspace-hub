---
name: crossprovider gemini pre-push-hooks-must-parse-stdin-refs-not-staged-
description: Pre-push hooks must parse stdin refs, not staged files
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [git-hooks, pre-push, workspace-hub]
---

Git pre-push hooks receive `<local_ref> <local_oid> <remote_ref> <remote_oid>` via stdin; must use `git diff <remote_oid>..<local_oid>` to find changed files. Checking staged changes (git diff --cached) belongs in pre-commit, not pre-push, and will silently miss committed changes.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
