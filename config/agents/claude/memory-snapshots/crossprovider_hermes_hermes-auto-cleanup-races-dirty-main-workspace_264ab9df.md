---
name: crossprovider hermes hermes-auto-cleanup-races-dirty-main-workspace
description: Hermes auto-cleanup races dirty main workspace
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-workflow, git-safety, parallel-agents]
---

Hermes background cleanup processes revert commits on `main` within minutes if another machine has pushed conflicting state. For execution slots that land commits, use clean worktrees + feature branches rather than dirty `main`; isolates work and avoids silent revert hazards.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
