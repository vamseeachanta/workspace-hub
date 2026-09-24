---
name: crossprovider gemini work-item-archival-metadata-pattern
description: Work item archival metadata pattern
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [work-queue, archival, metadata]
---

Archiving completed work items includes: moving to archive/<YYYY-MM> directory, setting status:done, adding completed_at timestamp (ISO format), updating commit field with latest commit hash. Mark all follow-up work items as ARCHIVED with their completion commits to provide traceability. Enables clear historical record and prevents re-opening completed work.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
