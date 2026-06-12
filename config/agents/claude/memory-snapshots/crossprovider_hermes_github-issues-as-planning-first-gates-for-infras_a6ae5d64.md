---
name: crossprovider hermes github-issues-as-planning-first-gates-for-infras
description: GitHub issues as planning-first gates for infrastructure decisions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [github-workflow, infrastructure, planning]
---

Tier-1 repo placement decisions use planning-only GitHub issues (#2754–#2757, one per machine) with `status:needs-plan` label before any filesystem moves. Pattern: create issue, draft plan, run adversarial review, post summary to GitHub, await approval, then implement. Prevents unplanned moves.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
