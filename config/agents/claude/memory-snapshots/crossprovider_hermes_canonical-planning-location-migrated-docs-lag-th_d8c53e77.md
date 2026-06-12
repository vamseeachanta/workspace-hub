---
name: crossprovider hermes canonical-planning-location-migrated-docs-lag-th
description: Canonical planning location migrated; docs lag the change
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [documentation-drift, canonical-paths, batch-audit]
---

Active issue plans moved from `.planning/` to `docs/plans/`, but multiple live docs still claim `.planning/` is canonical. Approval marker is now `.planning/plan-approved/<issue-number>.md` + GitHub label. Expect recurrence: batch-audit docs mentioning `.planning/phases`, `specs/wrk/`, `.claude/work-queue/` as live paths; all are legacy.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
