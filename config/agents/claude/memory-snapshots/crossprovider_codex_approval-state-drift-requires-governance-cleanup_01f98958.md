---
name: crossprovider codex approval-state-drift-requires-governance-cleanup
description: Approval-state drift requires governance cleanup on real gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-process, stale-state, governance, codex-adversarial]
---

When live GitHub approval labels diverge from current draft state, plans must explicitly flag the drift and include cleanup language for real approval-gate surfaces (GitHub `status:` labels, local `.planning/plan-approved/` markers). Documentation rows alone are insufficient; must handle the actual mechanism that will block/unblock work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
