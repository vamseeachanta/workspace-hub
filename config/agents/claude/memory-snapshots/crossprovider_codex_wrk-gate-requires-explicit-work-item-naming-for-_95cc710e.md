---
name: crossprovider codex wrk-gate-requires-explicit-work-item-naming-for-
description: WRK gate requires explicit work-item naming for approval
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [work-queue, governance, gate-enforcement]
---

The workspace enforces a hard gate: review/plan execution cannot begin without explicit approval that names the WRK id (e.g., 'Approve WRK-640'). Generic intent statements like 'review and implement' do not satisfy the gate. Codex correctly blocked execution when approval was missing, even when the plan was complete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
