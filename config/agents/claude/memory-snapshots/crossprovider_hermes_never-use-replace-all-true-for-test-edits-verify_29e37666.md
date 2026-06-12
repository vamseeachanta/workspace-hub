---
name: crossprovider hermes never-use-replace-all-true-for-test-edits-verify
description: Never use replace_all=True for test edits; verify with git diff
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, git, patch, verification]
---

When patching test files, contextual matching (3+ line context) is required; replace_all=True corrupts unrelated tests in the file. Always verify each patch with `git diff` before running the test file—once tests pass, move to the next file. This prevents silent regressions from glob replacements.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
