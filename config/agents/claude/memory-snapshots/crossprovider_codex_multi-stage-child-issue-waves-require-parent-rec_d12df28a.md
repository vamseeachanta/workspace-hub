---
name: crossprovider codex multi-stage-child-issue-waves-require-parent-rec
description: Multi-stage child-issue waves require parent reconciliation after completion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [issue-triage, workflow-gates, parent-child-sync]
---

Parent completeness artifacts and approval markers can become stale after all child issues complete (e.g., #116 still listed DNV issues as blockers after all #756-#763 were implemented). Reconciliation work is needed post-wave to update parent state and unblock downstream control-loop issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
