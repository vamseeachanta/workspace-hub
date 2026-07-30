---
name: crossprovider codex fuse-mounted-git-operations-spawn-orphaned-proce
description: FUSE-mounted git operations spawn orphaned processes that block updates
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [git, fuse, environment, infrastructure]
---

Slow FUSE I/O causes git status/merge probes to create zombie processes blocking subsequent updates. Workaround: explicitly terminate known probe PIDs, then retry with lower-I/O paths (partial clone, git plumbing commands).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
