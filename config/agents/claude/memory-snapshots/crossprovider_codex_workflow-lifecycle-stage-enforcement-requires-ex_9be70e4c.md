---
name: crossprovider codex workflow-lifecycle-stage-enforcement-requires-ex
description: Workflow lifecycle stage enforcement requires executable gates, not doc-only updates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-gates, stage-enforcement, work-queue-lifecycle]
---

Stage 5→6 transitions in the work-queue lifecycle are routinely skipped (agents jump to Stage 6/7 review). Documentation updates alone won't fix this; the check must be implemented in the executable entrypoint (scripts/agents/plan.sh) and reject progress until required artifacts exist.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
