---
name: crossprovider codex untracked-code-doesn-t-satisfy-branch-carry-or-c
description: Untracked code doesn't satisfy branch carry or CI gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, ci-gates, commit-hygiene, verification]
---

A script that is executable and functional still fails CI if its parent directory is untracked. Verify `git diff --cached --name-status` includes the file, not just `ls` + `test -x`. Sessions showed legal-sanity-scan.sh existing but `scripts/legal/` untracked caused MAJOR failures until staged.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
