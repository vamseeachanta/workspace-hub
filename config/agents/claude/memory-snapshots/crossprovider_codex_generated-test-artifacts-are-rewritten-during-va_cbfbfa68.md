---
name: crossprovider codex generated-test-artifacts-are-rewritten-during-va
description: Generated test artifacts are rewritten during validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-infrastructure, git-workflow]
---

Generated test artifacts like `coverage-results.json` are rewritten during validation runs. These must be restored before push if uncommitted to maintain clean worktree state and avoid unintended scope drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
