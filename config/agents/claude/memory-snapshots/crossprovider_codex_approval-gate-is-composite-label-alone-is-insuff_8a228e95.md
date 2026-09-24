---
name: crossprovider codex approval-gate-is-composite-label-alone-is-insuff
description: Approval gate is composite: label alone is insufficient
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, approval-gate, workspace-hub-specific]
---

The `status:plan-approved` GitHub label is necessary but not sufficient for implementation. Verify three conditions: (1) label present, (2) revision-bound marker (`.planning/plan-approved/<issue>.md` or issue-comment bound to a specific commit), and (3) all upstream/blocking issues resolved. Missing any one blocks implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
