---
name: crossprovider hermes generated-state-files-should-not-be-committed-us
description: Generated state files should not be committed; use git restore to clean
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [state-files, git-hygiene, cleanup]
---

Files like `.claude/state/` generated during validation/readiness runs can linger in staged changes. These should not be committed. Use `git restore -- .claude/state` to clean them before final staging/commit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
