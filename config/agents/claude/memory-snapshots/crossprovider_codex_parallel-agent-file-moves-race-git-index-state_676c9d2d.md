---
name: crossprovider codex parallel-agent-file-moves-race-git-index-state
description: Parallel agent file moves race git index state
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [parallel-agents, git-state, race-condition]
---

When parallel agents move files (e.g., working/WRK-X.md → done/WRK-X.md), git index can be stale, causing git to report a delete+new pair instead of a rename. Leads to untracked files. After parallel file operations, explicitly stage the move with `git add -A <file>` or verify file presence before assuming rename succeeded.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
