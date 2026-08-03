---
name: crossprovider codex sparse-checkout-silently-preserves-tracked-files
description: Sparse checkout silently preserves tracked files despite git rm --cached --sparse
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [git-sparse-checkout, index-management, worktree-pitfall]
---

When using `git rm --cached --sparse` to untrack files in a sparse working tree, the command may succeed but leave the file tracked in the index. Verify with `git ls-files --stage` after the operation. If a file remains tracked, amend the commit with `--sparse` flag or use `git rm --cached --force --sparse`. Otherwise the file remains tracked despite the CLI output's success, causing silent repository state drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
