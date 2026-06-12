---
name: crossprovider hermes governance-index-consistency-is-an-approval-bloc
description: Governance index consistency is an approval blocker
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [governance-consistency, index-integrity, metadata-sync]
---

The canonical plan index (docs/plans/README.md) must reflect actual plan file status and metadata. Stale index entries (e.g., "filed (no plan yet)" when plan exists, or "draft" when file says "plan-review") block approval and indicate incomplete governance workflow.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
