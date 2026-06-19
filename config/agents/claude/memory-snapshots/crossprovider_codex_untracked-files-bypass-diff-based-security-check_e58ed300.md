---
name: crossprovider codex untracked-files-bypass-diff-based-security-check
description: Untracked files bypass diff-based security checks
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [testing, security, git]
---

Commands like `git diff`, `legal-sanity-scan --diff-only`, and `git diff --check` only scan tracked/staged files. Session 2: implementation artifacts were untracked; legal scan passed but didn't review actual new file contents. Session 8: untracked script/test files needed explicit file-level review, not diff inspection. When files untracked, scope verification explicitly to those files.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
