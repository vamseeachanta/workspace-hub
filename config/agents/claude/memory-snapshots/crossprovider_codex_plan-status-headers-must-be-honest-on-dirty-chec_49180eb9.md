---
name: crossprovider codex plan-status-headers-must-be-honest-on-dirty-chec
description: Plan status headers must be honest on dirty checkouts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [status-honesty, approval-markers, draft-state]
---

When plans sit in dirty workspaces with uncommitted artifacts and stale .planning/plan-approved/N.md markers, status headers must conservatively label the state (e.g., `draft (local/uncommitted)`) rather than inheriting false confidence from prior approval markers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
