---
name: crossprovider hermes plan-scope-overlaps-need-explicit-ownership-boun
description: Plan scope overlaps need explicit ownership/boundary decisions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, multi-issue-coordination, scope-boundaries]
---

When two issues share boundary (e.g., #354 and #355 both touch `info()`), plans must make explicit ownership decisions: "info() responsibility stays with #354" or "CLI responsibility in #355." Vague boundaries lead to conflicts and rework.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
