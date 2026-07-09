---
name: crossprovider codex approval-gate-and-publication-gate-must-be-docum
description: Approval gate and publication gate must be documented as distinct in downstream issue messaging
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [process, documentation, gates]
---

Downstream issues may block on 'approval' but not understand that approval of validators ≠ publication readiness. Wording like 'approved to implement' can mislead into thinking 'approved to publish'. Pattern: separate gates in issue body: 'Unblock after #61 implemented validators + passing-command' vs. 'Public publication blocked until #63 has canary evidence'.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
