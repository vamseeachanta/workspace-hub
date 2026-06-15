---
name: crossprovider codex git-index-testing-validate-tracked-status-not-ju
description: Git index testing: validate tracked status, not just file existence
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, git-safety, regression-prevention]
---

Tests using `(path).exists()` pass when files exist in the working tree but are untracked. For regression testing that files remain staged/committed, use `git ls-files --stage` to validate index membership explicitly. Catch repeated "staged files dropped" hazards before they ship.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
