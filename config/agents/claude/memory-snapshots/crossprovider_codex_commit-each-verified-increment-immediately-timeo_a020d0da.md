---
name: crossprovider codex commit-each-verified-increment-immediately-timeo
description: Commit each verified increment immediately; timeout risk is real
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [workflow, git, incremental-commit]
---

Long sessions can be killed by timeout before final commit. Work survives only if committed to worktree. Commit each meaningful verified step as it completes, not one bundled commit at the end. Incremental commits on feature branches are fine and preferred.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
