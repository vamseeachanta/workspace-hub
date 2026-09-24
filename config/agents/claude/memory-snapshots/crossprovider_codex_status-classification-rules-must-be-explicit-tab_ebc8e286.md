---
name: crossprovider codex status-classification-rules-must-be-explicit-tab
description: Status classification rules must be explicit tables, not prose
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [spec-clarity, planning, cross-review, documentation]
---

Prose descriptions like 'repo_status is fail when critical>0' create implementation ambiguity and multiple review iterations. Write a decision matrix before coding: rows=conditions (critical count, high count, lock status), columns=resulting status/exit-code/gate-action. Ambiguous specs block convergence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
