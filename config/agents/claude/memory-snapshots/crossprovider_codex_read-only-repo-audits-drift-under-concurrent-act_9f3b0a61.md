---
name: crossprovider codex read-only-repo-audits-drift-under-concurrent-act
description: Read-only repo audits drift under concurrent activity
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [audit, concurrent-work, state-consistency, large-repo]
---

Large monorepo state surveys can become stale while running if parallel processes are active (new worktrees appear, files stage, refs update). Final snapshot pass needed for reliable evidence; single-point-in-time state from early in audit is unreliable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
