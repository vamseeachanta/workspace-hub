---
name: crossprovider codex scope-binding-via-mandatory-mission-statement-an
description: Scope binding via mandatory Mission statement and runtime enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-pattern, scope-control, work-queue]
---

Work queue items require a mandatory one-sentence `## Mission` statement at intake (Stage 1) that defines the scope boundary. During execution (Stage 10), re-read the Mission before coding; if any discovered tasks fall outside it, capture them as separate WRK items rather than expanding scope. This pattern prevents scope creep by binding implementation to pre-approved boundaries and making out-of-scope work explicit and trackable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
