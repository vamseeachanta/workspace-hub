---
name: crossprovider codex multi-deliverable-workflow-refactors-need-explic
description: Multi-deliverable workflow refactors need explicit scope locks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scope-management, workflow-contracts, decision-locking]
---

When a single WRK spans multiple workflow phases (e.g., Phase 1 hard-gate rollout + Phase 2 review-packaging), lock specific decisions that must not be narrowed without explicit user re-approval. Document which constraints are immovable, preventing later scope creep that undermines the original intent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
