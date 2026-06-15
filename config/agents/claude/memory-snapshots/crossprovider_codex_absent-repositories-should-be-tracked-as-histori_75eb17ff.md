---
name: crossprovider codex absent-repositories-should-be-tracked-as-histori
description: Absent repositories should be tracked as historically_moved_not_currently_present
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [inventory, audit-trail, state-tracking]
---

When repositories are reported in issue comments as sibling=git but are absent on probe, classify them as `historically_moved_not_currently_present` with source issue/comment provenance, prior_claim, latest_probe status, and a warning flag. This preserves audit trail and prevents silent data-state transitions. Example: mkt-a, OGManufacturing (which also needs runtime-access removal).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
