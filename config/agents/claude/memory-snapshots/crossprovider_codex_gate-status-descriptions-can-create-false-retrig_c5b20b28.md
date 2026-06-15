---
name: crossprovider codex gate-status-descriptions-can-create-false-retrig
description: Gate-status descriptions can create false retriggers
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [planning, github-issues, status-management]
---

Stale wording like "must move to status:pending" when the issue is already in status:plan-review causes reviewers to re-apply transitions or question gate flow. Status-description text should be factual snapshots, not prescriptive actions. Update plan text immediately after the issue state changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
