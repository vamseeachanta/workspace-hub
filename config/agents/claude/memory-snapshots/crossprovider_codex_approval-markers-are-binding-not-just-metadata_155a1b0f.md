---
name: crossprovider codex approval-markers-are-binding-not-just-metadata
description: Approval markers are binding, not just metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [approval-workflow, git-tracking]
---

Presence/absence of `.planning/plan-approved/<issue>.md` files is execution-relevant evidence, equivalent to GitHub label state. Absence means "not approved" even if label says `status:plan-approved`. Approval markers should never be auto-created; they reflect user intent gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
