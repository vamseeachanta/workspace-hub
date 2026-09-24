---
name: crossprovider codex pathological-git-tree-entries-with-backslashes-c
description: Pathological git tree entries with backslashes cause Windows checkout failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-tree-hygiene, windows-portability]
---

Git can store filenames with literal backslashes (e.g., `path\with\backslashes`), visible via `git ls-tree -r HEAD`. These entries cause `fatal: invalid path` errors on Windows checkouts. Resolution requires tree hygiene to rename or remove pathological entries from the commit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
