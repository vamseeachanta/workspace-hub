---
name: crossprovider codex validation-only-mode-when-prior-commits-exist-on
description: Validation-only mode when prior commits exist on issue branch
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-workflow, execution-mode, verification, multi-lane]
---

When an issue branch already has pushed commits or an open PR (verified via `gh pr view` + remote state), switch to validation + self-review mode instead of implementing. Run narrow verification tests, check CI status, post evidence comment with branch SHA and blockers—do not rewrite or broaden scope. Pattern: inspect-first, avoid duplication.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
