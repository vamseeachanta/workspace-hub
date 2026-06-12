---
name: crossprovider hermes github-issues-serve-as-planning-first-decision-l
description: GitHub issues serve as planning-first decision ledgers before operations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning-pattern, decision-record, github-workflow]
---

Before any filesystem operations (repo moves, clones, deletions), create GitHub planning issues to record the decision and constraints. Issues #2754–#2757 exemplify this: machine tier-1 repo placement was recorded as planning issues with specific labels (`machine:*`, `status:needs-plan`, `domain:workstations`) before any filesystem action.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
