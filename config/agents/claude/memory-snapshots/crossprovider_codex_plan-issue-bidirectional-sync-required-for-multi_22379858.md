---
name: crossprovider codex plan-issue-bidirectional-sync-required-for-multi
description: Plan-issue bidirectional sync required for multi-child epics
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [planning, github-issues, consistency, review]
---

When a plan defines child GitHub issues with dependencies, changes must update BOTH the plan file AND the live issue bodies. A plan can be internally consistent while live issues carry stale scope/dependency text, leading implementation agents astray. Verify live issue text against the plan's stated graph during adversarial review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
