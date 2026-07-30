---
name: crossprovider codex untracked-files-don-t-travel-in-git-diffs
description: Untracked files don't travel in git diffs
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [git, defect, fixcomplete]
---

Fixes that create new untracked files (e.g., scripts/legal/) need to be staged and committed. A passing script execution doesn't prove the fix is durable if the script itself remains untracked; it won't travel in a PR or final branch state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
