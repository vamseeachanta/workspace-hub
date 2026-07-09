---
name: crossprovider codex status-transition-checklists-cannot-reference-un
description: Status transition checklists cannot reference unbuilt artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [planning, readiness, gates, status]
---

Readiness checklists for status transitions (e.g., draft→plan-review) cannot include scanning or validation of components that don't exist yet (e.g., "scan with the new scanner before approval"). Either use existing validators or defer validation to post-approval implementation verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
