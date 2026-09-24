---
name: crossprovider gemini audit-universe-mismatch-as-a-planning-blocker
description: Audit Universe Mismatch as a Planning Blocker
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [audit, governance, reconciliation]
---

When multiple detectors or scoring systems cover the same domain (e.g., duplicate detection vs. usage scoring), their inclusion/exclusion policies and universes differ implicitly. Audits must explicitly reconcile or choose one universe; leaving ambiguous creates report inconsistency and false gaps.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
