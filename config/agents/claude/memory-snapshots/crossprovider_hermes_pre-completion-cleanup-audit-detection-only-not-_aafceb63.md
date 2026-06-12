---
name: crossprovider hermes pre-completion-cleanup-audit-detection-only-not-
description: Pre-completion cleanup audit: detection-only, not auto-delete
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [completion-gate, hygiene, audit-pattern]
---

Run cleanup audit before marking work complete to report (not remove) transient /tmp files, sibling-checkout accumulations, draft state, lock/trash. Audit categories: in-repo drift, scratch artifacts, session handoff state. Agent reports findings; user decides next action.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
