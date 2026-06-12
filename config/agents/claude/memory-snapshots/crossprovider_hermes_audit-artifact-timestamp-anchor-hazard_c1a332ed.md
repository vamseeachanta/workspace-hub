---
name: crossprovider hermes audit-artifact-timestamp-anchor-hazard
description: Audit artifact timestamp anchor hazard
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit, temporal-logic, data-integrity]
---

When regenerating audit reports with a new `generated_at` timestamp, logs with event timestamps between the old and new generated_at get retroactively excluded from future 'recent activity' filters. Anchor recent-activity cutoff to previous audit's generated_at (not 'now'), and document the temporal window explicitly in output to avoid silent data loss across audit cycles.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
