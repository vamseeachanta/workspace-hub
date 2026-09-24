---
name: crossprovider codex marker-based-plan-approval-with-label-marker-syn
description: Marker-based plan approval with label/marker sync issues
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-gate, workflow-pattern, governance]
---

Plan approval is enforced by `.planning/plan-approved/` markers, not just `status:plan-approved` labels. Many issues carry the label without corresponding markers, indicating workflow sync problems. Marker presence is the actual approval gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
