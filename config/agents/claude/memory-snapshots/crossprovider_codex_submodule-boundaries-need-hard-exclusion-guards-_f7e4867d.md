---
name: crossprovider codex submodule-boundaries-need-hard-exclusion-guards-
description: Submodule boundaries need hard exclusion guards and post-change verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, monorepo, refactoring, verification]
---

Multi-directory repos must hard-exclude submodules in every command (not assumed) and validate post-change to prevent accidental contamination. Paired with explicit verification matrix (grep assertions, bash -n, smoke tests, boundary checks) before approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
