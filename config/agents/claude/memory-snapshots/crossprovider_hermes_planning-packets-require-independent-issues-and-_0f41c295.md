---
name: crossprovider hermes planning-packets-require-independent-issues-and-
description: Planning packets require independent issues and user decisions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, execution-readiness, user-decisions]
---

Each planning packet must identify independent issues (no blocking dependencies within packet), define scope, assign provider/machine route, and list explicit user decision checkpoints (not inferred from issue body). Include hygiene gates (test coverage, path/import validation, CI parity) and review route (planner → reviewer → adversarial pass).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
