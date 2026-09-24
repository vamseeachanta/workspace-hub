---
name: crossprovider codex distributed-status-state-github-labels-vs-local-
description: Distributed status state (GitHub labels vs. local files) signals corruption
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [audit-pattern, state-sync, multi-agent-coordination]
---

When GitHub issue label ('status:plan-approved') diverges from local plan file status (README row says 'draft'), treat it as a red flag for confused state. No enforced single source of truth. Next agent cannot reliably act without re-checking primary sources. Sync local status to issue label in the same commit that changes the label.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
