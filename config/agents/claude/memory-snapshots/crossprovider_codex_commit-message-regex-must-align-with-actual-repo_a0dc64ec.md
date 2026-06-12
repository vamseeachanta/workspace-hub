---
name: crossprovider codex commit-message-regex-must-align-with-actual-repo
description: Commit-message regex must align with actual repo hook enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-workflow, enforcement, regex]
---

Plans inventing strict regex like `^(feat|fix|chore|...)` conflict with real repo policies that allow `build`, `ci`, `merge`, `revert`, `wip` and do not always require `type(scope)` syntax. Derive the acceptable pattern from the canonical hook source (check-commit-msg.sh, git-workflow.md), not from isolated design.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
