---
name: crossprovider codex declarative-job-catalog-with-role-filters-beats-
description: Declarative job catalog with role filters beats per-machine crontabs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow, declarative, operations, multi-machine]
---

Centralizing workflow definitions in one role-tagged catalog avoids 'adding a job requires N places' problem. Each machine materializes only its role subset via reconciler. Scales better than separate crontabs and ensures new jobs land consistently across fleet.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
