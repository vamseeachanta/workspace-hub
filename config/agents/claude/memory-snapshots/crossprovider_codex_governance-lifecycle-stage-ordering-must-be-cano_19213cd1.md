---
name: crossprovider codex governance-lifecycle-stage-ordering-must-be-cano
description: Governance lifecycle stage ordering must be canonical across all SKILL.md
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [governance-conflict, lifecycle-ordering, skill-assessment]
---

When multiple skills define stage sequences (e.g., work-queue, workflow-gatepass, work-queue-workflow), verify they agree on canonical stage numbers and ordering before assessment or merge decisions. Stage-order conflicts hide in SKILL.md prose and only surface when detailed cross-reference analysis forces re-read. WRK-1010 found work-queue-workflow defined Stage 2=Triage/Stage 3=Resource Intel, conflicting with work-queue and workflow-gatepass canonical order.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
