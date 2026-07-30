---
name: crossprovider codex approved-plan-topology-must-be-validated-against
description: Approved plan topology must be validated against live state before RED
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [planning, approval-gates, topology-validation]
---

An approved delivery plan can be topologically impossible if baseline assumptions have shifted (e.g., five wrapper failures already present on main). Stop before production edits, revise the plan, and re-secure approval. Discovery that invalidates the approved topology requires plan-review, not proceeding with implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
