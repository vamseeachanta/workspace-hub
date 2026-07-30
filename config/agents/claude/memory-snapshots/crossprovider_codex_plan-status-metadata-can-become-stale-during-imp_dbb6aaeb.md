---
name: crossprovider codex plan-status-metadata-can-become-stale-during-imp
description: Plan status metadata can become stale during implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [documentation, validation, drift]
---

Issue plan files sometimes carry outdated status fields (e.g., 'Status: plan-review' when the issue is already marked implementation-ready). Requires explicit closeout validation that schema/plan/approval-marker states are consistent, not just visual inspection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
