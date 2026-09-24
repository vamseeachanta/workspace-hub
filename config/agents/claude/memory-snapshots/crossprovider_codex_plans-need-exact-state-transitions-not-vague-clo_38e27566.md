---
name: crossprovider codex plans-need-exact-state-transitions-not-vague-clo
description: Plans need exact state transitions, not vague close/complete language
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, lifecycle, issue-workflow, closure]
---

Vague phrases like "close the issue" or "post a comment" hide lifecycle ambiguity (child issue #756: does `status:plan-review` → `status:plan-approved` only? Does `dispatch:ready` get removed? Does parent #116 get unblocked?). Specify exact label/state changes for all affected issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
