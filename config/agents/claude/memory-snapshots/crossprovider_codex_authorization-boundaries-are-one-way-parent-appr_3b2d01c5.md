---
name: crossprovider codex authorization-boundaries-are-one-way-parent-appr
description: Authorization boundaries are one-way; parent approval does not approve child implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [governance, authorization, gate-independence]
---

Plan #74 explicitly states: "Approval of parent #3559 or publisher #1045 will not approve this implementation." Child implementations require their own separate review and approval gate, even if parent is approved. Production readiness may wait for upstream signals (e.g., publication receipt), but approval is local.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
