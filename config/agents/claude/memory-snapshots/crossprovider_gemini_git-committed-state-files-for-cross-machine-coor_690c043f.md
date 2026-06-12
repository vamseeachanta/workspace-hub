---
name: crossprovider gemini git-committed-state-files-for-cross-machine-coor
description: Git-committed state files for cross-machine coordination
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [multi-machine, state-management, git-coordination]
---

Multi-machine workflows coordinate via `.claude/state/` directories (candidates/, corrections/, patterns/, session-signals/) committed to git. Each machine contributes its own learnings; a single coordinator machine (ace-linux-1) pulls and processes them all nightly.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
