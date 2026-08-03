---
name: crossprovider codex late-commit-clusters-must-be-audited-for-acciden
description: Late commit clusters must be audited for accidental index contamination
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, CI, governance]
---

When 6+ commits land at the end of a feature branch, verify they altered only intended surfaces (CI, evidence, docs). Concurrent worktree activity can accidentally sweep unrelated working-tree state into staged index. Distinguish committed state from parallel-session residue.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
