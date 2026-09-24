---
name: crossprovider codex parallel-read-only-audit-before-interactive-clea
description: Parallel read-only audit before interactive cleanup decisions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, filesystem, workflow, interactive-audit]
---

Different folder classes (repos, worktrees, artifacts) benefit from independent parallel audits (dirty state, active processes, stashes, origin refs) before gating user approval; reconcile evidence once all audits complete to avoid serial bottleneck.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
