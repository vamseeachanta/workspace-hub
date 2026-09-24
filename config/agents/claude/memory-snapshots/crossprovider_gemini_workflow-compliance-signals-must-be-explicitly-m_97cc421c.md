---
name: crossprovider gemini workflow-compliance-signals-must-be-explicitly-m
description: Workflow compliance signals must be explicitly measured, not inferred
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow, governance, measurement, workspace-hub]
---

WRK lifecycle compliance tracking requires actual signal emissions from logging scripts (e.g., `scripts/work-queue/log-user-review-*.sh`), not inferred stage completion or heuristics. Only explicit stage signals count for compliance ledger accuracy.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
