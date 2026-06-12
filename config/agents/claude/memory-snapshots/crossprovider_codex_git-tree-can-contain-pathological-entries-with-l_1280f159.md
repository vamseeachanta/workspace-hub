---
name: crossprovider codex git-tree-can-contain-pathological-entries-with-l
description: Git tree can contain pathological entries with literal backslashes
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git, windows, tree-hygiene]
---

Some repositories have git tree entries with literal backslashes in filenames (not forward slashes), causing Windows checkout failures with exit code 128 and "invalid path" messages. Verify with `git ls-tree -r HEAD` and filter or rename during tree health audits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
